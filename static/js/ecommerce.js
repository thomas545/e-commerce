$(document).ready(function() {
  // Auto Search
  var searchForm = $(".search-form")
  var searchInput = searchForm.find("[name='q']")
  var searchBtn = searchForm.find("[type='submit']")
  var typingTimer;
  var typingInterval = 500

  searchInput.keyup(function(event) {
    clearTimeout(typingTimer)
    typingTimer = setTimeout(performsearch, typingInterval)
  })

  searchInput.keydown(function(event) {
    clearTimeout(typingTimer)
  })

  function displaySearch() {
    searchBtn.addClass("disabled")
    searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching ....")
  }

  function performsearch () {
    displaySearch()
    var query = searchInput.val()
    setTimeout(function () {
      window.location.href = "/search/?q=" + query
    }, 1000)

  }

  // Cart + Add - remove Product
  var productForm = $('.form-product-ajax')
  productForm.submit(function (event){
    event.preventDefault();
    // console.log("Form Don't Work Yet");
    var thisForm = $(this);
    // var actionPoint = thisForm.attr('action');
    var actionPoint = thisForm.attr('data-point');
    var httpMethod = thisForm.attr('method');
    var formData = thisForm.serialize();
    var submitSpan = thisForm.find(".submit-span")
    var cartCount = $('.cart-count')

    $.ajax({
      url: actionPoint,
      method: httpMethod,
      data: formData,
      success: function(data){
        if (data.added){
          submitSpan.html("<button type='submit' class='btn btn-outline-warning' >Remove</button>")
        } else {
          submitSpan.html("<button type='submit' class='btn btn-outline-success' >Add to cart</button>")
        }
        cartCount.text(data.cartCount)
        var currentPath = window.location.href
        if (currentPath.indexOf("cart") != -1) {
          refreshCart()
        }
      },
      error: function(errorData){
        $.alert({
          title : "Oops",
          content : "An Error Occurred",
          theme : "modern",
        });
      }

    })

    function refreshCart() {
      console.log("in cart");
      var cartTable = $(".cart-table")
      var cartBody = cartTable.find(".cart-body")
      // cartBody.html("<h1>Changed</h1>")
      var productRows = cartBody.find(".cart-product")
      var current_url = window.location.href

      var cartUrl = '/cart/api/cart/';
      var cartMethod = "GET";
      var data = {};

      $.ajax({
        url: cartUrl,
        method: cartMethod,
        data: data,
        success: function (data){
          var hiddenCartItemRemove = $(".cart-item-remove-form")
          if (data.products.length > 0){
            productRows.html(" ")
            i = data.products.length
            $.each(data.products, function (index, value) {
              var newCartItem = hiddenCartItemRemove.clone()
              newCartItem.css("display", "block")
              newCartItem.find(".cart-item-product-id").val(value.id)
              cartBody.prepend("<tr><th scope=\"row\">" + i + "</th><td><a href='" +
              value.url + "'>" + value.name + "</a>" + newCartItem.html() + "</td><td>" + value.price + "</td></tr>")
                i --
                // window.location.href = current_url
            })
            cartBody.find(".cart-subtotal").text(data.subtotal)
            cartBody.find(".cart-total").text(data.total)

          } else {
            window.location.href = current_url
          }

        },
        error: function (errorData) {
          $.alert({
            title : "Oops",
            content : "An Errr Occurred",
            theme : "modern",
          });
        }
      })




    }


  });
});
