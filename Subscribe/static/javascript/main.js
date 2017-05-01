// var youtube_video_ids = ['7lkhrw-Mj8g','-RcTmH_vdTw'];
// var curr_id = 0;
// var youtube_width = '640';
// var youtube_height = '390';
// if($(window).width()<700){
//   youtube_width = '300';
//   youtube_height = '150'
// }
// var player;
//   function onYouTubeIframeAPIReady() {
//     player = new YT.Player('player', {
//       height: youtube_height,
//       width: youtube_width,
//       videoId: youtube_video_ids[curr_id],
//       events: {
//         'onReady': onPlayerReady,
//       }
//     });
//   }
//   function onPlayerReady(event) {
//      // event.target.playVideo();
// }
//
//    function stopVideo() {
//       player.stopVideo();
//     }
    function startAnimations() {
      $('div.text').textillate({
        selector: '.texts.active',
        loop: true,
        minDisplayTime: 3400,
        initialDelay: 0,
        autoStart: true,
        inEffects: [],
        outEffects: [],
        in: {
          effect: 'fadeIn',
          delayScale: 1.5
        },
        out: {
          effect: 'fadeOut',
          delayScale: 1.5
        },
        type: 'char'
      });
      $('div#slider figure').addClass('active');
    }
      $('nav > ul > li').on('click',function(){
          var flag = 0;
          var a = $('div#slider figure.active').css("left");
          var b = $(window).width();
          var c = parseInt(a)/b;
          var time = 5*18/100;
          if(c == 0)
          {
            $('div#slider figure').css('animation-play-state','paused');
            $('div.text span *').css('animation-play-state','paused');
          }
          else{
            if(c < 0 && c >= -1){

              var d = time*(1 + c)*1000;
              console.log(c,time,d);
              setTimeout(function(){
                $('div#slider figure').css('animation-play-state','paused');
                $('div.text span *').css('animation-play-state','paused');
              },d);
            }
             if(c < -1 && c >= -2){
              var d = time*(2 + c)*1000;
              console.log(c,time,d);
              setTimeout(function(){
                $('div#slider figure').css('animation-play-state','paused');
                $('div.text span *').css('animation-play-state','paused');
              },d);
            }
             if(c < -2 && c >= -3){
              var d = time*(3 + c)*1000;
              console.log(c,time,d);
              setTimeout(function(){
                $('div#slider figure').css('animation-play-state','paused');
                $('div.text span *').css('animation-play-state','paused');
              },d);
            }
          }
      });
