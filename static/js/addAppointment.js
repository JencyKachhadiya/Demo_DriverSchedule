const csrftoken = $("[name=csrfmiddlewaretoken]").val();

var validator = new FormValidator({
    "events": ['blur', 'input', 'change']
}, document.forms[0]);
// on form "submit" event
document.forms[0].onsubmit = function (e) {

    var submit = true,
        validatorResult = validator.checkAll(this);
    console.log(validatorResult);

    return !!validatorResult.valid;
};
// on form "reset" event
document.forms[0].onreset = function (e) {
    validator.reset();
};
// stuff related ONLY for this demo page:
$('.toggleValidationTooltips').change(function () {
    validator.settings.alerts = !this.checked;
    if (this.checked)
        $('form .alert').remove();
}).prop('checked', false);

function setEndDateTime(dataRow){
    startDateTime = $("#"+dataRow.id).val()
    var formattedDatetime = startDateTime.replace("T", " ");
    $('#endDateTime').attr('min', formattedDatetime);
    $('#endDateTime').removeAttr('readonly')
}

$('#startDateTime').on('change',function(){
    setTruckAndDriver(this);
});

function setTruckAndDriver(dataRow){
    startDateTime = $("#startDateTime").val()
    endDateTime = $("#endDateTime").val()
    console.log(startDateTime,endDateTime);
    if(startDateTime && endDateTime){
        $.ajax({
            url: "/appointment/getTruckAndDriver/",
            method: "POST",
            data: {
                'startDateTime' : startDateTime,
                'endDateTime' : endDateTime
            },
            beforeSend: function (xhr) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (data) {
                data.availableTrucksList.forEach(function (item) {
                    $("#truckNo").append(
                      '<option value="' + item['adminTruckNumber'] + '">' + item['adminTruckNumber'] + "</option>"
                    );
                });
                data.availableDriversList.forEach(function (item) {
                    $("#driverName").append(
                      '<option value="' + item['driverId'] + '">' + item['driverId']+'-' + item['name'] + "</option>"
                    );
                });
                $('#addDriver').removeAttr('disabled')
                $('#addTruck').removeAttr('disabled')
            },
        });
    }
}

function checkOrigin(){
    let originName = $("#origin").val()
    if(originName){
        $("#origin").removeClass('isInvalid')
        $.ajax({
            url: "/appointment/getOriginDetails/",
            method: "POST",
            data: {
                'originName' : originName
            },
            beforeSend: function (xhr) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
            },
            success: function (data) {
                if(data.status == true){
                    $('#originAddress').val(data.origin.address);
                    $('#originPhone').val(data.origin.phone)
                    $('#originPersonOnName').val(data.origin.personOnName)
                    $('#originLatitude').val(data.origin.lat)
                    $('#originLongitude').val(data.origin.long)
                    $('#originAddress').attr('readonly',true)
                    $('#originPhone').attr('readonly',true)
                    $('#originPersonOnName').attr('readonly',true)
                    $('#originLatitude').attr('readonly',true)
                    $('#originLongitude').attr('readonly',true)
                    $('#locationDiv').addClass('d-none')
                    $('#errorMsgForOrigin').addClass('d-none')
                }else{
                    $('#originAddress').val('')
                    $('#originPhone').val('')
                    $('#originPersonOnName').val('')
                    $('#originLatitude').val('')
                    $('#originLongitude').val('')
                    $('#errorMsgForOrigin').val('')
                    $('#originAddress').removeAttr('readonly')
                    $('#originPhone').removeAttr('readonly')
                    $('#originPersonOnName').removeAttr('readonly')
                    $('#originLatitude').removeAttr('readonly')
                    $('#originLongitude').removeAttr('readonly')
                    $('#errorMsgForOrigin').removeClass('d-none')
                    $('#locationDiv').removeClass('d-none')
                    $("#originAddVal").val(1)
                }
            },
        });
        
    }else{
        $("#origin").addClass('isInvalid')
    }
}

function openBox(checked,id){
    if ($(`#${checked.id}`).prop('checked')) {
        $(`#${id}`).removeAttr('disabled')
    }else{
        $(`#${id}`).attr('disabled', true)
    }
}