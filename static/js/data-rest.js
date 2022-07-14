function update(url){
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