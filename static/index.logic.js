var indexData = {}
var state = {}
$.getJSON( "/index/JSON", function( data ) {indexData = data} )

function trimStr(name, max) {
  var strLen = name.length
  if  ( strLen > max ){
    name = name.substr(0, max - 3) + "..."
  }
  return name
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length,c.length);
        }
    }
    return "";
}

function renderProducts( categoryId ){
  var productHTML = ""
  products = indexData.categories[categoryId].products
  Object.keys(products).forEach(function(productId){
    productHTML += "<li data-product-id='" + productId + "' class='product-li'>"
    productName = trimStr(products[productId].name, 25)
    var priceNameLen = (productName + products[productId].price).length
    var dots = ".".repeat(Math.max(38 - priceNameLen, 0))
    productHTML += productName + " " + dots + " $" + products[productId].price
    productHTML += "</li>\n"
    console.log(document.cookie.user_id, products[productId].user_id)
    if ( getCookie("user_id") === products[productId].user_id ){
      productHTML += "<a class='delete-link' href='/delete/product/" + productId + "/" + products[productId].name + "'>❌</a>"
      productHTML += "<a class='edit-link' href='/edit/product/" + productId + "'>✏️</a>"
    }
  })

  $( "#products-list" ).html(productHTML)

  var old_link = $( "#new-product-link" )[0].href
  old_link = old_link.split("/")
  old_link.pop()
  old_link.pop()
  var new_link = old_link.join("/") + "/" + categoryId + "/"
  $("#new-product-link")[0].href = new_link
  $("#product-header").html(trimStr(indexData.categories[categoryId].name, 20))
  productHoverHandler()
}

function renderDescription ( productId ){
  var descriptionHTML = ""
  product = indexData.categories[state.selectedCategory].products[productId]
  desc = product.description
  name = product.name
  price = product.price
  imgpath = product.imgpath
  $("#description-header").html(name)
  $("#product-description").html(desc)
  $("#product-img").attr('src', imgpath)
  $("#product-img").show()
}

function categoryHoverHandler(){
  $( ".category-li" ).hover( function(){
    var categoryId = $( this ).data( "category-id" )
    state.selectedCategory = categoryId
    renderProducts( categoryId)
    $("#description-header").html("")
    $("#product-description").html("")
    $("#product-img").hide()
  })
}

function productHoverHandler(){
  $( ".product-li" ).hover( function(){
    var productId = $( this ).data( "product-id" )
    renderDescription( productId )
  })
}

$( document ).ready(function() {
    categoryHoverHandler()
});
