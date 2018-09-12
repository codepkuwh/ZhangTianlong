document.getElementById("result").setAttribute("style", "height: 660px; font-size:28px;");
document.getElementById("print_output").setAttribute("style", "height: 630px; font-size:28px;");
document.querySelector(".content_right").prepend(document.querySelector(".run_btn"));
document.querySelector(".run_btn").style.left = "10%";
document.querySelector(".run_btn").style.top = "2%";
document.querySelector(".clear_btn").style.top = "2%";
document.querySelector(".clear_btn").style.left = "22%";
var MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver;
var target = document.getElementById("print_output"); 
var observer = new MutationObserver(function(mutations) {  
  mutations.forEach(function () {
      if (document.getElementById("print_output").innerHTML.indexOf("<br>")!== -1) return;
    else document.getElementById("print_output").innerHTML = document.getElementById("print_output").innerHTML.replace(/\n/g,'<br>');
    }); 
}); 
var config = {attributes: true, childList: true};
observer.observe(target, config);
