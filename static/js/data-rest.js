function api_update(url){
    var form = $('#data');
    console.log(form.serializeArray())
    $.ajax({
        type: 'PUT',
        url: url,
        data: form.serializeArray(),
        success: function (data) {
            console.log(data)
            // location.reload();
        },
        error: function (err) {
            alert("Failed");
        }
    })
}

function api_delete(url){
    $.ajax({
        type: 'DELETE',
        url: url,
        success: function (data) {
            location.reload();
        },
        error: function (err) {
            alert("Failed");
        }
    })
}