window.setTimeout(function () {
  window.location.reload();
}, 100000);

$(document).ready(function() {
    // Fetch the initial table
    $(document).ready(function() {
    $('#example').DataTable( {
            "lengthMenu": [
            [25, 50, 100, 200, -1],
            [25, 50, 100, 200, "All"]
        ],
        "order": [[ 3, "desc" ]],
        "iDisplayLength": -1,
        "ajax": "update.json",
        "columns": [
            { "data": "index" },
            { "data": "name" },
            { "data": "current" },
            { "data": "bought" },
            { "data": "quantity" },
            { "data": "rsi" },
            { "data": "profit" },
            { "data": "profit_per" },
            { "data": "link",
         "render": function(data, type, row, meta){
            if(type === 'display'){
                data = '<a href="' + data + '">' + "Exchange Homepage" + '</a>';
            }
            return data;
         }
      }
        ]
    } );
} );


    // Fetch every 5 seconds
    setInterval(update, 700);
});


function update(){
$.getJSON("update.json", function(result){
$("#example").dataTable().fnClearTable();
 $.each(result, function(i, field){
    $('#example').dataTable().fnAddData(field);
  });
  });



}

