$(document).ready(function () {
  var stripeFormModule = $(".stripe-payment-form")
  var stripeToken = stripeFormModule.attr("data-token")
  var stripeNextUrl = stripeFormModule.attr("data-next-url")
  var stripeTitleBtn = stripeFormModule.attr("data-btn-title") || "Add Payment"
  var stripeTemplate = $.templates("#stripeTemplate")
  var stripeTemplateData = {
      publish_key: stripeToken,
      next_url: stripeNextUrl,
      btn_title: stripeTitleBtn
  }
  var stripeTemplateHtml = stripeTemplate.render(stripeTemplateData)
  stripeFormModule.html(stripeTemplateHtml)


    // Create a Stripe client.
  var paymentForm = $(".payment-form")
  if (paymentForm.length > 1) {
    alert("Only One Payment Operation")
    paymentForm.css('display', 'none')
  } else if (paymentForm.length == 1) {
    var pubKey = paymentForm.attr('data-token')
    var nextUrl = paymentForm.attr('data-next-url')

    var stripe = Stripe(pubKey);

    // Create an instance of Elements.
    var elements = stripe.elements();

    // Custom styling can be passed to options when creating an Element.
    // (Note that this demo uses a wider set of styles than the guide below.)
    var style = {
    base: {
      color: '#32325d',
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: 'antialiased',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
    };

    // Create an instance of the card Element.
    var card = elements.create('card', {style: style});

    // Add an instance of the card Element into the `card-element` <div>.
    card.mount('#card-element');

    // Handle real-time validation errors from the card Element.
    card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
      displayError.textContent = event.error.message;
    } else {
      displayError.textContent = '';
    }
    });

    // // Handle form submission.
    // var form = document.getElementById('payment-form');
    // form.addEventListener('submit', function(event) {
    // event.preventDefault();
    //
    // stripe.createToken(card).then(function(result) {
    //   if (result.error) {
    //     // Inform the user if there was an error.
    //     var errorElement = document.getElementById('card-errors');
    //     errorElement.textContent = result.error.message;
    //   } else {
    //     // Send the token to your server.
    //     stripeTokenHandler(nextUrl, result.token);
    //
    //   }
    // });
    // });

    // New Handle form submission.

  var form = $('#payment-form');
  var btnLoad = form.find(".btn-load")
  var btnLoadDefaultHtml = btnLoad.html()
  var btnLoadDefaultClasses = btnLoad.attr("class")

  form.on('submit', function(event) {
    event.preventDefault();
    // get the btn
    // display new btn ui
    var $this = $(this)
    // btnLoad = $this.find('.btn-load')
    btnLoad.blur()
    var loadTime = 1500
    var currentTimeout;
    var errorHtml = "<i class='fa fa-warning'></i> An error occured"
    var errorClasses = "btn btn-danger disabled my-3"
    var loadingHtml = "<i class='fa fa-spin fa-spinner'></i> Loading..."
    var loadingClasses = "btn btn-success disabled my-3"

    stripe.createToken(card).then(function(result) {
      if (result.error) {
        // Inform the user if there was an error
        var errorElement = $('#card-errors');
        errorElement.textContent = result.error.message;
        currentTimeout = displayBtnStatus(
                              btnLoad,
                              errorHtml,
                              errorClasses,
                              1000,
                              currentTimeout
                          )


      } else {
        // Send the token to your server
        currentTimeout = displayBtnStatus(
                              btnLoad,
                              loadingHtml,
                              loadingClasses,
                              10000,
                              currentTimeout
                          )

        stripeTokenHandler(nextUrl, result.token);

      }
    });
  });


  function displayBtnStatus(element, newHtml, newClasses, loadTime, timeout){
      // if (timeout){
      //   clearTimeout(timeout)
      // }
      if (!loadTime){
        loadTime = 1500
      }
      //var defaultHtml = element.html()
      //var defaultClasses = element.attr("class")
      element.html(newHtml)
      element.removeClass(btnLoadDefaultClasses)
      element.addClass(newClasses)
      return setTimeout(function(){
          element.html(btnLoadDefaultHtml)
          element.removeClass(newClasses)
          element.addClass(btnLoadDefaultClasses)
      }, loadTime)
  }


    function redirectPath(nextpath, timeofset) {
      if (nextpath) {
        setTimeout(function() {
          window.location.href = nextpath
        }, timeofset)
      }
    }


    function stripeTokenHandler(nextUrl, token){

      var paymentUrl = "/billing/create/payment/"
      var data = {"token":token.id}

      $.ajax({
        url : paymentUrl,
        method : "POST",
        data : data,
        success: function (data) {
          var successMsg = data.message || "Your Payment Was Successfuly!"
          card.clear()
          if (nextUrl) {
            successMsg = successMsg + "<br/><br/><i class='fa fa-spin fa-spinner'></i> Redirecting..."
          }
          if ($.alert) {
            $.alert(successMsg)
          } else {
            $.alert(successMsg)
          }
          btnLoad.html(btnLoadDefaultHtml)
          btnLoad.attr('class', btnLoadDefaultClasses)
          redirectPath(nextUrl, 1500)
        },
        error: function (error) {
          // console.log(error);
          $.alert({title: "An error occured", content:"Please try adding your card again."})
          btnLoad.html(btnLoadDefaultHtml)
          btnLoad.attr('class', btnLoadDefaultClasses)
        }

      })


    }

  }
})

// Submit the form with the token ID.
// function stripeTokenHandler(token) {
// // Insert the token ID into the form so it gets submitted to the server
// var form = document.getElementById('payment-form');
// var hiddenInput = document.createElement('input');
// hiddenInput.setAttribute('type', 'hidden');
// hiddenInput.setAttribute('name', 'stripeToken');
// hiddenInput.setAttribute('value', token.id);
// form.appendChild(hiddenInput);
//
// // Submit the form
// form.submit();
// }
