
// var unsaved = false;



// $(":input").change(function () { //triggers change in all input fields including text type
//     unsaved = true;
// });

// $('#save').click(function () {
//     alert("save");
//     unsaved = false;
// });

// function unloadPage() {
//     if (unsaved) {
//         return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
//     }
// }
// window.onbeforeunload = unloadPage;




$(document).ready(function () {

    var unsaved = false;


    $('#save').click(function () {

        unsaved = false;

    });



    $(window).bind('beforeunload', function () {
        if (unsaved) {
            return "You have unsaved changes on this page. Do you want to leave this page and discard your changes or stay on this page?";
        }
    });

    // Monitor dynamic inputs
    $(document).on('change', ':input', function () { //triggers change in all input fields including text type
        unsaved = true;
    });




});

