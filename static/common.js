// 看是否有数据
function is_data_get(ret) {
    for (var i = 0; i < ret['sensor_data_average_list'].length; i++) {
        if (ret['sensor_data_average_list'][i] !== 0) {
            return false;  // 表示有非零数据，即内有内容
        }
    }
    return true;  // 内容全为零
}


// 显示echarts的dom和移动到该位置
function focus_echarts_div(target_div) {
    document.getElementById(target_div).style.display = "block";  // 显示echarts的dom
    let target_div_top = $('#' + target_div).offset().top;  // 获得echarts容器距离顶部的高度
    $('html,body').animate({
        scrollTop: target_div_top
    }, 500); // 动画滑动
}


// 隐藏echarts的dom
function hide_echarts_div(target_div) {
    document.getElementById(target_div).style.display = 'none';  // 隐藏echarts的dom
}