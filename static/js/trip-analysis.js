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

  $(`input[name="checkVal"]`).click(function () {
    var checkVal = $(this).val();
    $(".multiselect-dropdown").css("display", "none");
    $(`#${checkVal}`)
      .next(".multiselect-dropdown")
      .css("display", "inline-block");
  });

  // Download
  $(`#download`).click(function () {
    const csrftoken = $("[name=csrfmiddlewaretoken]").val();
    if (checkDateValid()) {
      var data = {
        startDate: $("#startDate").val(),
        endDate: $("#endDate").val(),
      };
      var checkedVal = $(`input[name="checkVal"]:checked`).val();
      var checkValData = $(`#${checkedVal}`).val();

      if (checkedVal == "clientIdVal") {
        var info = {
          tables: ["Client"],
          values: checkValData,
        };
      } else if (checkedVal == "driverIdVal") {
        var info = {
          tables: ["Driver"],
          values: checkValData,
        };
      } else if (checkedVal == "truckNoVal") {
        var info = {
          tables: ["Truck"],
          values: checkValData,
        };
      } else if (checkedVal == "basePlantVal") {
        var info = {
          tables: ["basePlant"],
          values: checkValData,
        };
      } else {
        var info = {
          tables: ["all"],
          values: null,
        };
      }

      data.tables = info.tables;
      data.values = info.values;

      console.log(data.values);

      $.ajax({
        type: "POST",
        url: "/Invoice_analysis/analysis/download/", // Replace with the actual URL
        data: data,
        beforeSend: function (xhr) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        },
        success: function (data) {
          console.log(data); // Process the data received from the server
        },
      });
    }
  });

  // Analysis
  $(`#analysis`).click(function () {
    const csrftoken = $("[name=csrfmiddlewaretoken]").val();
    if (checkDateValid()) {
      var data = {
        startDate: $("#startDate").val(),
        endDate: $("#endDate").val(),
      };
    }
  });
});
