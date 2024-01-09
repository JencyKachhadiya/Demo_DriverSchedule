const csrftoken = $("[name=csrfmiddlewaretoken]").val();

$(document).ready(function () {
  $("#datatable-buttons").DataTable();
});

function clearInputs() {
  $("#filterForm input").remove();
  $('#filterForm').append(`<input type="text" hidden id="verifiedInput" name="verifiedInput" value="">`)
  $('#filterForm').append(`<input type="text" hidden id="clientInput" name="clientInput" value="">`)
  $('#filterForm').append(`<input type="text" hidden id="startDate" name="startDate" value="">`)
  $('#filterForm').append(`<input type="text" hidden id="endDate" name="endDate" value="">`)
}

function appendDataIntoTable(data) {
  $(".table tbody tr").remove();
  data.forEach((item) => {
    let verify = item.verified
      ? "fa-check text-success"
      : "fa-close text-danger";
    var row = "";
    row += `<tr>`;
    row += `<td><i class='fa ${verify}'></i></td>`;
    row += `<td>${item.truckNo}</td>`;
    row += `<td>${item.clientName_id}</td>`;
    row += `<td>${item.driverId_id}</td>`;
    row += `<td>${item.shiftDate}</td>`;
    row += `<td>${item.numberOfLoads}</td>`;
    row += `<td><a href="/account/driverTrip/edit/${item.id}/ " title="update"><i class="fa-solid fa-arrow-right" style="font-size:1.3rem"></i></a></td>`;
    row += `</tr>`;
    $(".table tbody").append(row);
  });
  return true;
}

function verifiedFilter(element, verified = 1) {
  $.ajax({
    url: "/account/verifiedFilter/",
    method: "POST",
    data: {
      verified: verified,
    },
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    },
    success: function (data) {
      if (appendDataIntoTable(data.data)) {
        clearInputs()
        $("#filterForm #verifiedInput").remove();
        inputElement = `<input type="text" hidden id="verifiedInput" name="verifiedInput" value="${verified}">`
        $('#filterForm').append(inputElement);

      }
    },
  });
}

function clientFilter(id) {
  $("#clientInput").val(id);
  $.ajax({
    url: "/account/clientFilter/",
    method: "POST",
    data: {
      id: id,
    },
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    },
    success: function (data) {
      if (appendDataIntoTable(data.data)) {
        clearInputs()
        $("#filterForm #clientInput").remove();
        inputElement = `<input type="text" hidden id="clientInput" name="clientInput" value="${id}">`
        $('#filterForm').append(inputElement);
      }
    },
  });
}


function dateConverter(date) {
  var dateObj = new Date(date);

  var year = dateObj.getFullYear();
  var month = dateObj.getMonth() + 1;
  var day = dateObj.getDate();
  console.log([year, month, day]);
  return [year, month, day];
}
function dateRangeFilter(startDate, endDate) {
  $.ajax({
    url: "/account/dateRangeFilter/",
    method: "POST",
    data: {
      startDate: dateConverter(startDate),
      endDate: dateConverter(endDate),
    },
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    },
    success: function (data) {
      if (appendDataIntoTable(data.data)) {
        clearInputs()
        $("#filterForm #startDate").remove();
        $("#filterForm #endDate").remove();
        inputElement1 = `<input type="text" hidden id="startDate" name="startDate" value="${dateConverter(startDate)}">`
        inputElement2 = `<input type="text" hidden id="endDate" name="endDate" value="${dateConverter(endDate)}">`
        $('#filterForm').append(inputElement1);
        $('#filterForm').append(inputElement2);
      }
    },
  });
}

function csvDownloadFilter() {
  var verified = $("#verifiedInput").val()
  var Cid = $("#clientInput").val()
  var startDate = $("#startDate").val()
  var endDate = $("#endDate").val()
  $.ajax({
    url: "/account/DriverTripCsv/",
    method: "POST",
    data: {
      verified: verified,
      id_: Cid,
      startDate: dateConverter(startDate),
      endDate: dateConverter(endDate),
    },
    beforeSend: function (xhr) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    },
    success: function (data) {
      // Create a temporary anchor element to trigger the download
      // var downloadAnchor = document.createElement('a');
      // downloadAnchor.href = data.url;  // The URL of the generated CSV file
      // downloadAnchor.download = csv_filename;  // Specify the desired filename
      // downloadAnchor.click();  // Trigger the download
    },
  });

}

