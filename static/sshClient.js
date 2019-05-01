/**
 * Created by Administrator on 2018/1/27.
 */

function  wsClient() {

}

// 生成url
wsClient.prototype._generateURL = function (options) {
    // 根据http协议区分WebSocket协议
    if (window.location.protocol === 'https:'){
        var protocol = 'wss://';
    }else{
        var protocol = 'ws://';
    }
    // ws://192.168.1.108:8000/fort/host/3/
    // return  protocol + window.location.host + '/info/auto_get_hum/' + encodeURIComponent(options.desc_id) + '/';
    let url = protocol + window.location.host + '/info/auto_get_data/' + encodeURIComponent(options.category_id) + '/' +encodeURIComponent(options.terminal_id)+'/';
    console.log(url);
    return  url;

};

// 接收数据
wsClient.prototype.connect = function (options) {
    // 获得ws连接地址
    var des_url = this._generateURL(options);

    // 根据不同的浏览器生成不同的WebSocket对象
    if (window.WebSocket) {
        this._ws_obj = new WebSocket(des_url);
    }
    else if (window.MozWebSocket) {  // 火狐浏览器
        this._ws_obj = new MozWebSocket(des_url);
    }
    else {
        options.onError('当前浏览器不支持WebSocket！');  // 执行options参数中的onError函数
        return ;
    }

    // 以下是WebSocket正规接收数据的四步骤中的三个步骤
    // 开始连接
    this._ws_obj.onopen = function () {
        options.onConnect();  // 执行options中的onConnect函数
    };

    // 获取服务端数据时触发
    this._ws_obj.onmessage = function (evt) {
        // 使用 JSON.parse() 方法将数据转换为 JavaScript 对象(dict-like)。
        var data = JSON.parse(evt.data.toString());  // 转为json数据
        console.log(evt.data);  // json数据 str
        console.log(data);  // js对象
        if (data.error !== undefined) {  // 如果内容附带错误信息
            options.onError(data.error);  // 执行options中的onError函数 这里.error表示等于['error']
        }
        else {
            options.onData(data);  // 执行options中的onData函数
        }
    };

    // 断开连接
    this._ws_obj.onclose = function () {
        options.onClose();  // 执行onClose函数
    };
};

// 发送数据
wsClient.prototype.send = function (data) {
    // 将一个JavaScript值(对象或者数组)转换为一个 JSON字符串
    console.log("send" + JSON.stringify({'data':data}));
    this._ws_obj.send(JSON.stringify({'data':data}));

};