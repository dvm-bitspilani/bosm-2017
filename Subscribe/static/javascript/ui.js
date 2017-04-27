$(document).ready(function(){






	$("#two footer .button").click(function(){
			$(".backdrop").fadeIn(1000);
				$(".backdrop").css('display','flex');

		curr_id = $(this).attr("list");

		player.loadVideoById({videoId:youtube_video_ids[curr_id],startSeconds:10,suggestedQuality:'large'});


	});

	$(".backdrop").click(function(){
      	stopVideo();
      	$(".backdrop").fadeOut();
	});

	// function adjust_footer_height(){
	// 	var footer_height_not = $("#two header").height() + $("#two section").height();
	// 	var window_height = $(window).height();
	// 	console.log("called");
	// 	if($(window).width() <900){
	// 		if(window_height - footer_height_not > 144){
	// 			$("#two footer").css({'height': window_height - footer_height_not + "px" ,
	// 								'position': 'absolute',
	// 								'bottom' : '0',
	// 								});
	// 		}else{
	// 			$("#two footer").css({'height': "auto" ,
	// 								'position': 'relative',
	// 								});
	// 		}

	// 	}else{
	// 		$("#two footer").css({'height':'20vh'})
	// 	}

	// }

	// adjust_footer_height();
	// $(window).resize(adjust_footer_height);


	// $('#two header label').click(function(){
	// 	console.log("called here")
	// 	var k = setTimeout(adjust_footer_height,100);
	// 	var n = setTimeout(adjust_footer_height,1000);
	//  });




});
