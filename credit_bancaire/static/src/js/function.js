
odoo.define("credit_bancaire.webScrapingFunction", function (require) {
    const core = require('web.core');
    var FormController = require('web.FormController');
    var clicked = false;
    FormController.include({
        _onButtonClicked: function (event) {
            if(event.data.attrs.id === "button_product"){
                clicked = true;
                console.log(clicked)
            }
            addElements();
            this._super(event);
            },
        _onSave: function (event) {
            var sup = this._super(event);
            console.log("_onSave");
            addElements();
            return sup;
        },
        _onEdit: function () {
        var sup = this._super();
        console.log("_onEdit");
        return sup;
    },
    });

    //product.appendChild(h1);

});
function  addElements(){
    var product = document.getElementById("products");
    const h1 = document.createElement("h5");
    const textNode = document.createTextNode("Products");
    h1.appendChild(textNode);
    product.appendChild(h1);
}

/**const fetch = require("node-fetch");
const getRawData = (URL) => {
   return fetch(URL)
      .then((response) => response.text())
      .then((data) => {
         return data;
      });
};

const getProductsList = async () => {
   const productRawData = await getRawData(URL);
   console.log(productRawData);
};**/