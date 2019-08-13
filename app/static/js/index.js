var deleteOrderUrl;

$(document).ready(function() {
  // Activate buy now button after page load
  $(".button-link").prop("disabled", false);

  // Go to first section
  $("#home-link").click(function(e) {
    e.preventDefault();
    $(".nav-link")[0].click();
  });

  // Section navigation
  $(".nav-link").click(function(e) {
    var targetId = e.target.id.split('-'),
    linkId = targetId[targetId.length - 1];
    $(".section.active").removeClass("active");
    $(".nav-link.active").removeClass("active");

    $("#section-" + linkId).addClass("active");
    $(this).addClass("active");
  });

  // Set global slide index
  $(".carousel").on('slid.bs.carousel', function () {
    var index = $(".section.active").find(".carousel-item.active").attr("index");
    $(".carousel-item.active").removeClass("active");
    $(".carousel-item[index=" + index + "]").addClass("active");
  });

  // Promo watermark background
  Array.from(document.querySelectorAll('.watermarked')).forEach(function(el) {
        el.dataset.watermark = (el.dataset.watermark + ' ').repeat(10000);
  });

  // Country modal
  $("#current-flag").click(function(e) {
    $('#countryModal').modal();
  });

  // Order modal
  $("#zar-button").click(function(e) {
    $('#orderModal').modal();
  });

  // za order form submit
  $("#za-order-form").submit(function(e) {

      e.preventDefault(); // avoid to execute the actual submit of the form.

      var form = $(this);
      var url = window.location.pathname;

      $.ajax({
        type: "POST",
        url: url,
        data: form.serialize(), // serializes the form's elements.
        success: function(data)
        {
          $.each(data, function (key, val) {
            $("#za-order-confirmation-form input[name=" + key + "]").val(val);
          });

          $("#confirm-list").html("");
          $("#za-order-form input, #za-order-form select").each(function(i, formInput){
            $("#confirm-list").append(
              "<li class='list-group-item'>" +
              " <b style='text-transform: capitalize;'>" + formInput.name + "</b> " +
              " <span id='" + formInput.name +  "-span' class='pull-right'>" +
                  formInput.value +
              " </span>" +
              "</li>"
            );
          });
          var totalCost = parseInt($("#za-order-form input[name=quantity]").val()) * 150;
          $("#cost-span").text("R" + totalCost);
          $("#confirm-list").append(
            "<li class='list-group-item pt-3' style='font-size: 1.5rem;'>" +
            " <b style='text-transform: capitalize;'><u>Price</u></b> " +
            " <span id='price-span' class='pull-right'>R" + totalCost + "</span>" +
            "</li>"
          );
          $('#orderModal').modal('hide');
          setTimeout(function(){ $('#orderConfirmModal').modal(); }, 500);
        }
      });
  });

  // Edit order details
  $("#order-back-btn").click(function(e) {
    var paymentId = $("#za-order-confirmation-form input[name='m_payment_id']").val();
    $.ajax({
      type: "POST",
      url: deleteOrderUrl,
      data: {'payment_id': paymentId},
      success: function (data) {console.log('Successfully deleted ' + paymentId);}
    });
    setTimeout(function(){ $('#orderModal').modal('show'); }, 500);
  });
});
