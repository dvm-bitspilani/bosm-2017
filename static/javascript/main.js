var youtube_video_ids = ['7lkhrw-Mj8g','avXQPMNIj-k'];
var curr_id = 0;
var youtube_width = '640';
var youtube_height = '390';
if($(window).width()<700){
  youtube_width = '300';
  youtube_height = '150'
}
var player;
  function onYouTubeIframeAPIReady() {
    player = new YT.Player('player', {
      height: youtube_height,
      width: youtube_width,
      videoId: youtube_video_ids[curr_id],
      events: {
        'onReady': onPlayerReady,
      }
    });
  }
  function onPlayerReady(event) {
     // event.target.playVideo();
}

   function stopVideo() {
      player.stopVideo();
    }
      $('div.text').textillate({
        selector: '.texts.active',
        loop: true,
        minDisplayTime: 3500,
        initialDelay: 0,
        autoStart: true,
        inEffects: [],
        outEffects: [],
        in: {
          effect: 'fadeIn',
        },
        out: {
          effect: 'fadeOut',
        },
        type: 'char'
      });
      $('div#slider figure').addClass('active');
      $('nav > ul > li').on('click',function(){
        if($('div.text').hasClass('active')){
          $('#slider figure').css('animation-play-state','paused');
          $('div.text span *').css('animation-play-state','paused');
        }
        else {
          $('#slider figure').css('animation-play-state','running');
          $('div.text span *').css('animation-play-state','running');
        }
        $('div.text').toggleClass('active');
      });
