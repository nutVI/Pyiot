# -*- coding: utf-8 -*-import jsonimport socketioimport loggingimport threadingfrom pyiot import eventimport requestsimport reclass Pyiot:    def __init__(self, host, qq, log_level=logging.INFO):        log_format = "%(asctime)s - %(levelname)s - %(message)s"        date_format = "%m/%d/%Y %H:%M:%S %p"        logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)        self.host = host        self.qq = qq        self.command_friend_dict = {}        self.command_group_dict = {}    def start(self):        """ 启动Pyiot """        def _():            sio = socketio.Client()            @sio.event            def connect():                """ 连接 """                sio.emit('GetWebConn', self.qq)  # 取得当前已经登录的QQ链接            @sio.on('OnGroupMsgs')            def on_group_msgs(message):                """ 监听群组消息 """                logging.info("收到群组消息")                print(message)                __on_message("group", message)            @sio.on('OnFriendMsgs')            def on_friend_msgs(message):                """ 监听好友消息 """                logging.info("收到好友消息")                print(message)                __on_message("friend", message)            def __on_message(type, message):                data = message["CurrentPacket"]["Data"]                message_content = data["Content"]                if type == "friend":                    for key, value in self.command_friend_dict.items():                        if re.match(key, message_content):                            value(event.Event(data))                elif type == "group":                    for key, value in self.command_group_dict.items():                        if re.match(key, message_content):                            value(event.Event(data))            @sio.on('OnEvents')            def on_events(message):                """ 监听事件 """                print(message)            sio.connect(self.host, transports=['websocket'])            logging.info(f"成功连接到{self.host}")            sio.wait()            sio.disconnect()        logging.info(f"Pyiot已启动")        thread = threading.Thread(target=_)        thread.setName("Thread - Listen for events")        thread.start()    def on_friend_text_command(self, c):        """ 装饰器 - 当消息开头是该字符串时调用该方法 """        print(f"register friend command [{c}]")        def decorate(func):            self.command_friend_dict[c] = func            return func        return decorate    def on_group_text_command(self, c):        """ 装饰器 - 当消息开头是该字符串时调用该方法 """        print(f"register group command [{c}]")        def decorate(func):            self.command_group_dict[c] = func            return func        return decorate    def reply(self, content, eve, at_user=0):        data = {            "toUser": eve.user,            "sendToType": eve.send_to_type,            "sendMsgType": "TextMsg",            "content": content,            "groupid": 0,            "atUser": at_user,            "replayInfo": None        }        headers = {'Content-Type': 'application/json'}        url = self.host + "v1/LuaApiCaller" if self.host[-1] == "/" else self.host + "/v1/LuaApiCaller"        params = {            "qq": self.qq,            "funcname": "SendMsg",            "timeout": 19        }        response = requests.post(url=url, headers=headers, data=json.dumps(data), params=params)        logging.debug(response.content)CRITICAL = 50FATAL = CRITICALERROR = 40WARNING = 30WARN = WARNINGINFO = 20DEBUG = 10NOTSET = 0def start(host, qq, log_level):    s = Pyiot(host, qq, log_level)    s.start()    return s