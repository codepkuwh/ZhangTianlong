document.getElementById("result").setAttribute("style", "height: 660px; font-size:28px;");
document.getElementById("print_output").setAttribute("style", "height: 650px; font-size:28px; word-wrap:break-word;");
document.querySelector(".content_right").setAttribute("style", "text-align: left;");
document.querySelector(".content_left").setAttribute("style", "width: 1400px;");
document.querySelector(".content_right").prepend(document.querySelector(".run_btn"));
document.querySelector(".run_btn").style.left = "10%";
document.querySelector(".run_btn").style.top = "2%";
document.querySelector(".clear_btn").style.top = "2%";
document.querySelector(".clear_btn").style.left = "22%";
var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
var target = document.getElementById("print_output"); 
var observer = new MutationObserver(function(mutations) {  
  mutations.forEach(function () {
    document.querySelector(".content_right p").setAttribute("style", "font-family: Consolas;");
      if (document.getElementById("print_output").innerHTML.indexOf("<br>")!== -1) return;
    else {document.getElementById("print_output").innerHTML = document.getElementById("print_output").innerHTML.replace(/\n/g,'<br>');
    }
    document.querySelector(".content_right p").setAttribute("style", "font-family: Consolas;");
    document.querySelector(".content_right p").innerHTML = document.querySelector(".content_right p").innerHTML.replace(/ /g, "&nbsp;");
    }); 
}); 
var config = {attributes: true, childList: true};
observer.observe(target, config);