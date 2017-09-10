$(document).ready(function(){
    $('.chk input').on('change',function(){
        var value = $(this).parent('td').next('td').html();
        value = parseInt(value);
        if(this.checked == true) {
            $("#amount").html( parseInt($("#amount").html()) + value );
        }
        else {
            $("#amount").html( parseInt($("#amount").html()) - value );
        }
    });
});