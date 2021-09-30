var api = "update_trade.json";
function onchange1()
{
api = "update_trade.json";
}
function onchange2()
{
api = "update_trade.json?filter=buy";
}
function onchange3()
{
api = "update_trade.json?filter=sell";
}

window.setTimeout(function () {
  window.location.reload();
}, 100000);

$(document).ready(function() {
    // Fetch the initial table
    $(document).ready(function() {
    $('#exampletable').DataTable( {
        "lengthMenu": [
            [25, 50, 100, 200, -1],
            [25, 50, 100, 200, "All"]],
        "iDisplayLength": 50,
        "ajax": api,
        "order": [[ 0, "desc" ]],
        "columns": [
            { "data": "index" },
            { "data": "name" },
            { "data": "current" },
            { "data": "bought" },
            { "data": "bought_busd" },
            { "data": "quantity" },
            { "data": "rsi" },
            { "data": "macd" },
            { "data": "profit" },
            { "data": "profit_per" },
            { "data": "action" },
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
    setInterval(update, 2000);
});


function update(){
$.getJSON(api, function(result){
$("#exampletable").dataTable().fnClearTable();
 $.each(result, function(i, field){
    $('#exampletable').dataTable().fnAddData(field);
  });
  });



}

