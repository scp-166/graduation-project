/**
 * Created by Administrator on 2018/1/27.
 */

function  sshClient() {

}

// 生成url
sshClient.prototype._generateURL = function (options) {
    // 根据http协议区分WebSocket协议
    if (window.location.protocol === 'https:'){
        var protocol = 'wss://';
    }else{
        var protocol = 'ws://';
    }
    // ws://192.168.1.108:8000/fort/host/3/
    // return  protocol + window.location.host + '/fort/host/' + encodeURIComponent(options.desc_id) + '/';
    return  protocol + window.location.host + '/echo/';

};

// 接收数据
sshClient.prototype.connect = function (options) {
    // 获得地址
    var des_url = this._generateURL(options);

    // 根据不同的浏览器生成不同的WebSocket
    if (window.WebSocket) {
        this._connection = new WebSocket(des_url);
    }
    else if (window.MozWebSocket) {  // 火狐浏览器
        this._connection = new MozWebSocket(des_url);
    }
    else {
        options.onError('当前浏览器不支持WebSocket！');  // term.write('错误:  ' + error + '\r\n')
        return ;
    }

    // 以下是WebSocket接收数据的四步骤
    this._connection.onopen = function () {
        options.onConnect();  // term.write('\r');
    };

    // 客户端接收服务端数据时触发
    this._connection.onmessage = function (evt) {
        // 使用 JSON.parse() 方法将数据转换为 JavaScript 对象。
        var data = JSON.parse(evt.data.toString());  // 转为json数据
        console.log(data);
        if (data.error !== undefined) {  // 如果内容附带错误信息
            options.onError(data.error);  // term.write('错误:  ' + error + '\r\n')
        }
        else {
            options.onData(data.data);  // term.write(data);
        }
    };

    this._connection.onclose = function () {
        options.onClose();  // term.write('对方断开了连接...');
    };
};

// 发送数据
sshClient.prototype.send = function (data) {
    // 将一个JavaScript值(对象或者数组)转换为一个 JSON字符串
    this._connection.send(JSON.stringify({'data':data}));

};