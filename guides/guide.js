(function(){
  "use strict";
  var $=function(i){return document.getElementById(i)};
  var y=$("yr");if(y)y.textContent=new Date().getFullYear();
  function theme(t){document.documentElement.dataset.theme=t;var m=document.querySelector('meta[name=theme-color]');if(m)m.content=t==="dark"?"#070C1E":"#f3f6fc"}
  theme(document.documentElement.dataset.theme||"dark");
  var tg=$("tg");if(tg)tg.addEventListener("click",function(){var t=document.documentElement.dataset.theme==="dark"?"light":"dark";theme(t);try{localStorage.setItem("ug_theme",t)}catch(e){}});
  /* YouTube: agar data-yt me video ID hai to embed, warna channel/videos page ka link */
  document.querySelectorAll(".vid").forEach(function(v){
    var id=(v.getAttribute("data-yt")||"").trim();
    if(/^[A-Za-z0-9_-]{11}$/.test(id)){
      v.innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+id+'" title="University Gyaan video" loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; picture-in-picture" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>';
    }
  });
})();
