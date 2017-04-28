var cossac = [
	{
		name: "Jayshil",
		img: "Jayshil.jpg",
		dept: "Sports Secretary",
		email: "sportssecretary@bits-bosm.org"
	},
	{
		name: "Siddharth",
		img: "Siddharth.jpg",
		dept: "Joint Sports Secretary",
		email: "Unknown"
	},
	{
		name: "Aman",
		img: "Untitled.jpg",
		dept: "Joint Sports Secretary",
		email: "Unknown"
	},
	{
		name: "Shreshtha",
		img: "Shreshtha.jpg",
		dept: "Joint Sports Secretary",
		email: "Unknown"
	},
	{
		name: "Pavan",
		img: "Pavan.jpg",
		dept: "For Scheduling and Events",
		email: "controls.bits-bosm.org"
	},
	
	{
		name: "Ashay",
		img: "Ashay.jpg",
		dept: "For Correspondence and Publicity",
		email: "pcr@bits-bosm.org"
	},
	
	{
		name: "Gautham",
		img: "Gautham.jpg",
		dept: "For Reception and Accomodation",
		email: "recnacc@bits-bosm.org"
	},
	{
		name: "vihang",
		img: "Vihang.jpg",
		dept: "Core Website",
		email: "webmaster@bits-bosm.org"
	}
	
];
var spons = [
	{
		logo: "epson.png",
		name: "Title Sponsor",
	},
	{
		logo: "pepsi.png",
		name: "Beverage Partner",
	},
	{
		logo: "manya.png",
		name: "Education Partner",
	},
	{
		logo: "saavn.png",
		name: "Music Streaming",
	},
	{
		logo: "adda.png",
		name: "Online Gaming",
	},
	{
		logo: "9xm.png",
		name: "Music Channel",
	},
	{
		logo: "du.png",
		name: "Online Media",
	}
];
for (var i in cossac) {
	cossacn = cossac[i];
	cossacul = $('ul.cards-list.cossac');
	cossacul.append('\
		<li>\
			<div class="proPic" style="background-image: url(/2017/static/images/cossac/'+cossacn.img+');background-size: cover;"></div>\
			<div class="info">\
				<label for="name" style="font-size:17px;">'+cossacn.name+'</label>\
				<label for="dept" class="dept" style="font-size:15px;padding:3px;text-align:center;">'+cossacn.dept+'</label>\
				<a href="mailto:'+cossacn.email+'"><label for="mail" style="font-size: 12px !important;">'+cossacn.email+'</label></a>\
			</div>\
		</li>\
	');
}
for (var i in spons) {
	sponsul = $('ul.cards-list.spons');
	sponsor = spons[i];
	sponsul.append('\
		<li>\
			<div class="proPic" style="background-image: url(/2017/static/images/sponsors/'+sponsor.logo+')"></div>\
			<div class="info">\
				<label for="name">'+sponsor.name+'</label>\
			</div>\
		</li>\
	');
}
	$(document).ready(function(){
			$('.popup').hide();
			$('.popup-wrapper').hide();
			$('.about-link').click(function(){
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.about').fadeIn()},500);
				});
			});
			$('.contact-link').click(function(){
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.contact').fadeIn()},500);
				});
			});
			$('.sponsors-link').click(function(){
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.sponsors').fadeIn()},500);
				});
			});
			$('.travel-link').click(function(){
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.travel').fadeIn()},500);
				});
			});
			$('.subscribe-link').click(function(){
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.subscribe').fadeIn()},500);
				});
			});
			$('.popup-wrapper').click(function(e){
				if (e.target == $(this)[0]){
				$('.popup').fadeOut('fast');
				$('.popup-wrapper').hide();
				$('#slider figure').css('animation-play-state','running');
				$('div.text span *').css('animation-play-state','running');
			}
			});
		});
