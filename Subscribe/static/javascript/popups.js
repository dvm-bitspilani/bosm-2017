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
		email: "+91-7733974342"
	},
	{
		name: "Aman",
		img: "Untitled.jpg",
		dept: "Joint Sports Secretary",
		email: "91-9714540571"
	},
	{
		name: "Shreshtha",
		img: "Shreshtha.jpg",
		dept: "Joint Sports Secretary",
		email: "+91-9873240714"
	},
	{
		name: "Jayesh",
		img: "Jayesh.jpg",
		dept: "For Sponsorship and Marketing",
		email: "sponsorship@bits-bosm.org"
	},
	{
		name: "Pavan",
		img: "Pavan.jpg",
		dept: "For Scheduling and Events",
		email: "controls@bits-bosm.org"
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
		name: "EPSON",
		title: "Title Sponsor",
	},
	{
		logo: "pepsi.png",
		name: "PEPSI",
		title: "Beverage Partner",
	},
	{
		logo: "manya.png",
		name: "Manya",
		title: "Education Partner",
	},
	{
		logo: "saavn.png",
		name: "Saavn",
		title: "Music Streaming",
	},
	{
		logo: "adda.png",
		name: "Adda52.com",
		title: "Online Gaming",
	},
	{
		logo: "9xm.png",
		name: "9XM",
		title: "Music Channel",
	},
	{
		logo: "du.png",
		name: "DU Beat",
		title: "Online Media",
	}
];
for (var i in cossac) {
	cossacn = cossac[i];
	cossacul = $('ul.cards-list.cossac');
	cossacul.append('\
		<li>\
			<div class="proPic" style="background-image: url(/2017/static/images/cossac/'+cossacn.img+');background-size: cover;"></div>\
			<div class="info">\
				<label for="name">'+cossacn.name+'</label>\
				<label for="dept" class="dept" style="padding:3px;text-align:center;">'+cossacn.dept+'</label>\
				<a href="mailto:'+cossacn.email+'"><label for="mail">'+cossacn.email+'</label></a>\
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
			<label for="spons">'+sponsor.name+'</label>\
			<label for="dept">'+sponsor.title+'</label>\
			</div>\
		</li>\
	');
}
	$(document).ready(function(){
			$('.popup').hide();
			$('.popup-wrapper').hide();
			function colorchange(){
				var a = $('div#slider figure.active').css("left");
				var b = $(window).width();
				var c = parseInt(a)/b;
				$('.green').removeClass('green');
				$('.red').removeClass('red');
				$('.purple').removeClass('purple');

				console.log(c);
				if(c == 0 || c<-2){
					return "red";
				}
				if(c < 0 && c>=-1)
				{
					return "green";
				}
				if(c <-1 && c>=-2)
				{
					return "purple";
				}
			}
			$('.about-link').click(function(){
				var color = colorchange();
				$('.about').addClass(color);
				$('section').hide();
				$('footer .buttons').fadeOut('fast');
				$('#toggle1:checked').click();
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.about').fadeIn()},500);
				});
			});
			$('.contact-link').click(function(){
				var color = colorchange();
				$('.contact').addClass(color);
				$('section').hide();
				$('footer .buttons').fadeOut('fast');
				$('#toggle1:checked').click();
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.contact').fadeIn()},500);
				});
			});
			$('.sponsors-link').click(function(){
				var color = colorchange();
				console.log(color);
				$('.sponsors').addClass(color);
				$('section').hide();
				$('footer .buttons').fadeOut('fast');
				$('#toggle1:checked').click();
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.sponsors').fadeIn()},500);
				});
			});
			$('.travel-link').click(function(){
				var color = colorchange();
				console.log(color);
				$('.travel').addClass(color);
				$('section').hide();
				$('footer .buttons').fadeOut('fast');
				$('#toggle1:checked').click();
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.travel').fadeIn()},500);
				});
			});
			$('.subscribe-link').click(function(){
				var color = colorchange();
				console.log(color);
				$('.subscribe').addClass(color);
				var col;
				if(color == "green"){
					col = "#00FED3";
				}
				if(color == "red"){
					col = "#EF3340";
				}
				if(color == "purple"){
					col = "#D68FD6";
				}
				$("#submit").css("background-color",col);
				$('.form_1 form').css("color",col);
				$('section').hide();
				$('footer .buttons').fadeOut('fast');
				$('#toggle1:checked').click();
				$('.popup-wrapper').show();
				$('.popup').fadeOut('fast',function(){
					setTimeout(function(){$('.subscribe').fadeIn()},500);
				});
			});
			$('.popup-wrapper').click(function(e){
				if (e.target == $(this)[0]){
				$('.popup').fadeOut('fast',function(){
					$('section').show();
				});
				$('.popup-wrapper').hide();
				$('footer .buttons').fadeIn('fast');
				$('#slider figure').css('animation-play-state','running');
				$('div.text span *').css('animation-play-state','running');
			}
			});
		});
