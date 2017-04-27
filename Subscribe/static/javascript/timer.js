var DRUM_TEXTURE = "";

// Assembiles are for grouping faces and other assembiles
function createAssembly() {
    var assembly = document.createElement("div");
    assembly.className = "threedee assembly";
    return assembly;
}

function createFace(w, h, x, y, z, rx, ry, rz, tsrc, tx, ty) {
    var face = document.createElement("div");
    face.className = "threedee face";
    face.style.cssText = PrefixFree.prefixCSS(
        "background: url(" + tsrc + ") -" + tx.toFixed(2) + "px " + ty.toFixed(2) + "px;" +
        "width:" + w.toFixed(2) + "px;" +
        "height:" + h.toFixed(2) + "px;" +
        "margin-top: -" + (h / 2).toFixed(2) + "px;" +
        "margin-left: -" + (w / 2).toFixed(2) + "px;" +
        "transform: translate3d(" + x.toFixed(2) + "px," + y.toFixed(2) + "px," + z.toFixed(2) + "px)" +
        "rotateX(" + rx.toFixed(2) + "rad) rotateY(" + ry.toFixed(2) + "rad) rotateY(" + rz.toFixed(2) + "rad);");
    return face;
}

function createTube(dia, height, sides, texture) {
    var tube = createAssembly();
    var sideAngle = (Math.PI / sides) * 2;
    var sideLen = dia * Math.tan(Math.PI/sides);
    for (var c = 0; c < sides; c++) {
        var x = Math.sin(sideAngle * c) * dia / 2;
        var z = Math.cos(sideAngle * c) * dia / 2;
        var ry = Math.atan2(x, z);
        face = createFace(sideLen + 1, height, x, 0, z, 0, ry, 0, texture, sideLen * c, 0);
        if(c%2 == 1) face.innerHTML = "<span></span>";
        else face.innerHTML = "<label>text</label>";
        tube.appendChild(face);
    }
    return tube;
}

function createBarrel() {
    var minht = 350;
    var ht = 0.8 * Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    if (ht < minht) ht = minht;
    var barrel = createTube(0.9*ht, 100, 30, DRUM_TEXTURE);
    document.barrel = barrel;
    return barrel;
}

function initTimer() {
document.querySelector('.assembly').style.width = 1.25*parseInt(document.querySelector('.assembly .face').style.width)+"px";
var times = ["3 Months","2 Months","1 Month","25 Days","20 Days","15 Days","2 Weeks","10 Days","1 Week","5 Days","4 Days","3 Days","2 Days","1 Day","0 Days"];
var labels = document.querySelectorAll("#timer label");
var today = new Date();
var bosm = new Date("08/27/2017");
var timeDiff = Math.abs(bosm.getTime() - today.getTime());
var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
if (diffDays >= 90) {var initial = 0;}
else if (diffDays >= 60) {var initial = 1;}
else if (diffDays >= 30) {var initial = 2;}
else if (diffDays >= 25) {var initial = 3;}
else if (diffDays >= 20) {var initial = 4;}
else if (diffDays >= 15) {var initial = 5;}
else if (diffDays >= 14) {var initial = 6;}
else if (diffDays >= 10) {var initial = 7;}
else if (diffDays >= 7) {var initial = 8;}
else if (diffDays >= 5) {var initial = 9;}
else if (diffDays == 4) {var initial = 10;}
else if (diffDays == 3) {var initial = 11;}
else if (diffDays == 2) {var initial = 12;}
else if (diffDays == 1) {var initial = 13;}
else {var initial = 14;}
var j = 0;
for (var i = initial; i < labels.length; i++) {
  labels[i-initial].innerHTML = times[i];
  j+=1;
}
for (i = 0; j < labels.length; j++, i++) {
  labels[j].innerHTML = times[i];
}

setTimeout(threedeestripes,2000)
}

function threedeestripes() {
  var faces = document.querySelectorAll('.face');
  var ct1 = faces[1].style.transform;
  var nt1 = ct1.replace(/Y\([^\)]*rad\)/,"Y(0.93rad)");
  var nt1 = nt1.replace(/X\([^\)]*rad\)/,"X(+0.02rad)");
  var ct19 = faces[29].style.transform;
  var nt19 = ct19.replace(/Y\([^\)]*rad\)/,"Y(-0.93rad)");
  var nt19 = nt19.replace(/X\([^\)]*rad\)/,"X(+0.02rad)");
  nt1 += " scale(1.5)";
  nt19 += " scale(1.5)";
  faces[1].style.transform = nt1;
  faces[0].querySelector('label').style.fontSize = "calc(3 * 1.8rem)";
  faces[1].querySelector('span').style.transform = "rotateZ(-90deg) rotateX(0deg) scaleX(0.5) scaleY(0.25)";
  faces[3].querySelector('span').style.transform = "rotateZ(-90deg) rotateX(0deg) scaleX(0.5) scaleY(0.15)";
  faces[29].querySelector('span').style.transform = "rotateZ(-90deg) rotateX(0deg) scaleX(0.5) scaleY(0.25)";
  faces[27].querySelector('span').style.transform = "rotateZ(-90deg) rotateX(0deg) scaleX(0.5) scaleY(0.15)";
  faces[29].style.transform = nt19;
}

window.onload = function() {
  document.querySelector('div#timer').appendChild(createBarrel());
  initTimer();
}

window.onresize = function() {
    //document.querySelector('.assembly').remove();
    // document.querySelector('div#timer').appendChild(createBarrel());
    // initTimer();
}
