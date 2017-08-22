$('document').ready(function(){
$('.button-collapse').sideNav({
      menuWidth: 300, // Default is 300
      edge: 'right', // Choose the horizontal origin
      closeOnClick: true, // Closes side-nav on <a> clicks, useful for Angular/Meteor
      draggable: true, // Choose whether you can drag to open on touch screens,
    }
  );

 $('.button-collapse').sideNav('show');
  // Hide sideNav
  $('.button-collapse').sideNav('hide');
 });