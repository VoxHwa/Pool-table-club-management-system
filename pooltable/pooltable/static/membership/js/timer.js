$(document).ready(function () {
    // 获取台球桌 ID 和绑定的会员 ID
    var tableId = $('#table-id').val();
    var memberId = $('#member-id').val();
  
    // 定义计时器相关变量
    var startTime = null;
    var pausedTime = null;
    var totalPausedTime = 0;
    var timerInterval = null;
  
    // 更新计时器显示时间
    function updateTime() {
      if (!startTime) {
        $('#usage-time').text('00:00:00');
        return;
      }
      var currentTime = new Date();
      var elapsed = currentTime.getTime() - startTime.getTime() - totalPausedTime;
      var hours = Math.floor(elapsed / (60 * 60 * 1000));
      var minutes = Math.floor((elapsed % (60 * 60 * 1000)) / (60 * 1000));
      var seconds = Math.floor((elapsed % (60 * 1000)) / 1000);
      var timeStr = hours.toString().padStart(2, '0') + ':' +
                    minutes.toString().padStart(2, '0') + ':' +
                    seconds.toString().padStart(2, '0');
      $('#usage-time').text(timeStr);
    }
  
    // 定义计时器操作函数
    function startTimer() {
      startTime = new Date();
      timerInterval = setInterval(updateTime, 1000);
      $('#start-btn').prop('disabled', true);
      $('#pause-btn').prop('disabled', false);
      $('#resume-btn').prop('disabled', true);
      $('#stop-btn').prop('disabled', false);
      $('#reset-btn').prop('disabled', true);
      $.post(
        "{% url 'membership:timer' %}",
        {table_id: tableId, member_id: memberId},
        function (data, status) {
          if (status !== 'success' || !data.success) {
            alert('计时器启动失败');
            stopTimer();
          }
        }
      );
    }
    
    function pauseTimer() {
      if (!startTime || pausedTime !== null) {
        return;
      }
      pausedTime = new Date();
      clearInterval(timerInterval);
      $('#start-btn').prop('disabled', true);
      $('#pause-btn').prop('disabled', true);
      $('#resume-btn').prop('disabled', false);
      $('#stop-btn').prop('disabled', false);
      $('#reset-btn').prop('disabled', false);
      $.post(
        "{% url 'membership:pause_timer' %}",
        {table_id: tableId},
        function (data, status) {
          if (status !== 'success' || !data.success) {
            alert('计时器暂停失败');
            resumeTimer();
          }
        }
      );
    }
    
    function resumeTimer() {
      if (!startTime || pausedTime === null) {
        return;
      }
      totalPausedTime += new Date() - pausedTime;
      pausedTime = null;
      timerInterval = setInterval(updateTime, 1000);
      $('#start-btn').prop('disabled', true);
      $('#pause-btn').prop('disabled', false);
      $('#resume-btn').prop('disabled', true);
      $('#stop-btn').prop('disabled', false);
      $('#reset-btn').prop('disabled', true);
      $.post(
        "{% url 'membership:resume_timer' %}",
        {table_id: tableId},
        function (data, status) {
          if (status !== 'success' || !data.success) {
            alert('计时器恢复失败');
            pauseTimer();
          }
        }
      );
    }
    
    function stopTimer() {
      if (!startTime || pausedTime !== null) {
        return;
      }
      clearInterval(timerInterval);
      startTime = null;
      totalPausedTime = 0;
      $('#start-btn').prop('disabled', false);
      $('#pause-btn').prop('disabled', true);
      $('#resume-btn').prop('disabled', true);
      $('#stop-btn').prop('disabled', true);
      $('#reset-btn').prop('disabled', false);
      $.post(
        "{% url 'membership:stop_timer' %}",
        {table_id: tableId},
        function (data, status) {
          if (status !== 'success' || !data.success) {
            alert('计时器停止失败');
          }
        }
      );
    }
    function resetTimer() {
      startTime = null;
      pausedTime = null;
      totalPausedTime = 0;
      clearInterval(timerInterval);
      $('#start-btn').prop('disabled', false);
      $('#pause-btn').prop('disabled', true);
      $('#resume-btn').prop('disabled', true);
      $('#stop-btn').prop('disabled', true);
      $('#reset-btn').prop('disabled', true);
      $.post(
        "{% url 'membership:reset_timer' %}",
        {table_id: tableId},
        function (data, status) {
          if (status !== 'success' || !data.success) {
            alert('计时器重置失败');
          }
        }
      );
      updateTime();
    }
  });    