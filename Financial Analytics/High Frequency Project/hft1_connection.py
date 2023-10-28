## hft1_connection.py

import hft1_pb2
import Authentication_pb2
import socket
import ssl
from datetime import datetime


def send_msg(sock, msg_bytes):
    # header = struct.pack('>H', len(msg_bytes))
    header = int.to_bytes(len(msg_bytes), 2, byteorder='big')
    sock.sendall(header + msg_bytes)
    return


def recv_all(sock, sz):
    bytes = sock.recv(sz)
    while len(bytes) < sz:
        bytes += sock.recv(sz-len(bytes))
    return bytes


def recv_msg(sock):
    header = recv_all(sock, 2)
    msg_len = int.from_bytes(header, byteorder='big')
    return recv_all(sock, msg_len)


def authorize(sock, login, password, stream_name):
    # generate login message
    login_msg = Authentication_pb2.LoginRequest(login=login,
                                                enc_password=password,
                                                stream_name=stream_name)
    # send login message
    print('Sending login message')
    send_msg(sock, login_msg.SerializeToString())
    # receive login-reply message and handle it
    raw_msg = recv_msg(sock)
    login_reply = Authentication_pb2.LoginReply()
    login_reply.ParseFromString(raw_msg)
    if login_reply.connection_status != Authentication_pb2.LoginReply.LoginErrorsEnum.OK:
        raise RuntimeError('Login failed: ' +
                           Authentication_pb2.LoginReply.LoginErrorsEnum.Name(login_reply.connection_status))
    # now we're logged in
    print('Logged in successfully as ', login)


def connect(host, port, login, password, stream_name,
            bidask_handler, orderexec_handler,
            catch_handler_errors=True):
    '''
    # main function, connects to server and invokes user specified handlers in the event loop
    ## bidask_handler is expected to have 4 arguments - bid_price, bid_vol, ask_price, ask_vol (integers)
    ## and to return 1 to buy@ask, -1 to sell@bid and 0 to do nothing
    ## orderexec_handler is expected to have 4 arguments:
    ### 1) side ('BOUGHT' or 'SOLD')
    ### 2) quantity (int)
    ### 3) price (int)
    ### 4) forced (bool) - TRUE when the order is initiated by the system
    ## and to return nothing
    '''
    result = {'problems': [],
              'n_signals': 0,
              'pnl': None,
              'total_trades': 0,
              'manual_trades': 0,
              'forced_trades': 0
              }
    # connect to server & authorize
    print(f'Connecting to {host}:{port}')
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            # make authorization
            authorize(ssock, login, password, stream_name)
            # event-loop for server messages
            while True:
                raw_msg = recv_msg(ssock)
                event_msg = hft1_pb2.Event()
                event_msg.ParseFromString(raw_msg)
                # check errors
                if event_msg.error:
                    problem = f'SERVER SENT: "{event_msg.error}"'
                    print(problem)
                    result['problems'] += (datetime.now(), problem)
                # process message from server
                if event_msg.HasField('bid_ask_event'):
                    try:
                        signal = bidask_handler(event_msg.bid_ask_event.bid0_price,
                                                event_msg.bid_ask_event.bid0_volume,
                                                event_msg.bid_ask_event.ask0_price,
                                                event_msg.bid_ask_event.ask0_volume)
                        assert signal in [-1, 0, 1]
                    except Exception as e:
                        if catch_handler_errors:
                            problem = f'Error inside bidask_handler: {e}. Forcing signal to 0'
                            print('!!!***   WARNING   ***!!!\n', problem, '\n!!!*******************!!!')
                            result['problems'] += (datetime.now(), problem)
                            signal = 0
                        else:
                            raise
                    if signal != 0:
                        signal_msg = hft1_pb2.Signal(signal = signal)
                        send_msg(ssock, signal_msg.SerializeToString())
                        result['n_signals'] += 1
                if event_msg.HasField('order_filled_event'):
                    # process new order execution
                    side = 'BOUGHT' if event_msg.order_filled_event.side == hft1_pb2.SideEnum.BUY \
                                    else 'SOLD'
                    try:
                        orderexec_handler(side,
                                          event_msg.order_filled_event.quantity,
                                          event_msg.order_filled_event.price,
                                          event_msg.order_filled_event.forced)
                    except Exception as e:
                        if catch_handler_errors:
                            problem = f'Error inside orderexec_handler: {e}'
                            print('!!!***   WARNING   ***!!!\n', problem, '\n!!!*******************!!!')
                            result['problems'] += (datetime.now(), problem)
                        else:
                            raise
                if event_msg.HasField('stream_end_event'):
                    # break from repeat-loop in case server stream ends
                    print('Stream has ended, goodbye!')
                    result['pnl'] = event_msg.stream_end_event.pnl
                    result['total_trades'] = event_msg.stream_end_event.total_trades
                    result['manual_trades'] = event_msg.stream_end_event.manual_trades
                    result['forced_trades'] = event_msg.stream_end_event.forced_trades
                    print('Some statistics:')
                    print('PnL=', result['pnl'])
                    print('Total trades: ', result['total_trades'])
                    print('Your trades: ', result['manual_trades'])
                    print('Forced trades: ', result['forced_trades'])
                    if event_msg.stream_end_event.HasField('score'):
                        result['score'] = event_msg.stream_end_event.score
                        print('Your score is ', result['score'], ' / 100')
                    print('Connection closed')
                    print(f'You sent total of {result["n_signals"]} signal(s) to server')
                    return result
