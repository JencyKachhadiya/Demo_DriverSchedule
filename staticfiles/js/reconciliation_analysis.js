const csrftoken = $("[name=csrfmiddlewaretoken]").val();

$(document).ready(function () {
  function checkDateValid() {
    var startDate = $("#startDate").val();
    var endDate = $("#endDate").val();
    flag = true;

    if (startDate == "") {
      $("#startDate").next(".errorMsg").removeClass("d-none");
      $("#startDate").addClass("isInvalid");
      flag = false;
    } else {
      $("#startDate").next(".errorMsg").addClass("d-none");
      $("#startDate").removeClass("isInvalid");
      flag = true;
    }

    if (endDate == "") {
      $("#endDate").next(".errorMsg").removeClass("d-none");
      $("#endDate").addClass("isInvalid");
      flag = false;
    } else {
      $("#endDate").next(".errorMsg").addClass("d-none");
      $("#endDate").removeClass("isInvalid");
      flag = true;
    }
    return flag;
  }

  var currentDate = new Date();
  var year = currentDate.getFullYear();
  var month = ("0" + (currentDate.getMonth() + 1)).slice(-2); // Adding 1 because months are zero-indexed
  var day = ("0" + currentDate.getDate()).slice(-2);
  var formattedDate = year + "-" + month + "-" + day;

  $("#startDate").attr("max", formattedDate);
  $("#endDate").attr("max", formattedDate);

  $("#startDate").on("change", function () {
    if ($(this).val() != "") {
      $("#endDate").removeAttr("readonly");
      $("#endDate").attr("min", $(this).val());
    }
  });

  // reconciliation
  $("#reconciliation").on("click", function (event) {
    event.preventDefault();
    if (checkDateValid()) {
      $("#signUpForm").submit();
    }
  }); 

});
