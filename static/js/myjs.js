$(document).ready(function(){
    $(".retry-btn").click(function(){
        $("#login-noti").css("display", "none");
        $("#upload-noti").css("display", "none");

    });

    //$("#change-password").click(function(){
        //$("#user-password").append("<div class="change-password-box">aaaaaaaa</div>");
    //});
    var filterTitle = document.getElementById("filter-type");
    if (filterTitle.innerHTML.includes("Any") == true){
        $("#filter-select").css("background-color", "black");
    }
});
var isAdvancedUpload = function() {
    var div = document.createElement('div');
    return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
  }();
var $form = $('.drag-box');

  if (isAdvancedUpload) {
    $form.addClass('has-advanced-upload');
  }
    