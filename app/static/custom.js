function login() {
  $(function(){
    if ($('#login_user').val() && $('#login_password').val()) {
      $.ajax({
          url: "login?" + $.param({
              "user": $('#login_user').val(),
              "password": $('#login_password').val(),
          }),
          type: "POST",
      })
      .done(function(data, textStatus, jqXHR) {
          if (data === 'successfuly logged in') {
            window.location.assign('/search?just_logged_in');
          } else if (data === 'login error') {
            $('#login_incorrect').removeClass('hidden')
            $('#form_login_user, #form_login_password').addClass('has-error')
          } else {
            alert(data);
          }
      })
      .fail(function(jqXHR, textStatus, errorThrown) {
          return;
      })
    }
  });
}

function verifier_enter(event, form, callback) {
  // fonction tirée de  http://stackoverflow.com/questions/14251676/
  var code = (event.keyCode ? event.keyCode : event.which);
  if(code === 13) {
    callback();
  }
}

function datepickers() {
  $(function() {
      $('.input-daterange input').each(function() {
        $(this).datepicker({language: "fr"});
      });
      $('.date').datepicker({language: "fr"});
    });
}