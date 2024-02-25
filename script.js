var InitialCount = -1;

const deleteProducts = async () => {
  const url = "http://127.0.0.1:5000/products"; 
  
  let res = await axios.get(url);
  responseText = await res.data;
  const products = responseText.products;

  for (let product of products) {
    const response = await axios.delete(
      `http://127.0.0.1:5000/products/${product.id}`
    );
  }
  location.reload();
  window.scroll({
    top: 0,
    left: 0,
    behavior: "smooth",
  });
};

const loadProducts = async () => {
  url = "http://127.0.0.1:5000/products";

  let res = await axios.get(url);
  responseText = await res.data;
  const products = responseText.products;
  var len = products.length;
  // console.log(products);
  // console.log(len);

  if (len > InitialCount + 1) {
    $("#1").css("display", "none");
    $("#home").css("display", "grid");
    $("#2").css("display", "grid");
    var payable = 0;
    const products = responseText.products;
    console.log(products);
    for (let product of products) {
      payable = payable + parseFloat(product.payable);
    }

    var product = products.pop();
    const x = `
      <section>
              <div class="card card-long animated fadeInUp once">
                  <img src="img/${product.id}.jpg" class="album">
                  <div class="span1">Product Name</div>
                  <div class="card__product">
                      <span>${product.name}</span>
                  </div>
                  <div class="span2">Per Unit</div>
                  <div class="card__price">
                      <span>${product.price} </span>
                  </div>
                  <div class="span3">Units</div>
                  <div class="card__unit">
                      <span>${product.taken} ${product.unit}</span>
                  </div>

                  <div class="span4">Payable</div>
                  <div class="card__amount">
                      <span>${product.payable}</span>
                  </div>
              </div>
          </section>
      <section>
      `;

    document.getElementById("home").innerHTML =
      document.getElementById("home").innerHTML + x;
    document.getElementById("2").innerHTML = "CHECKOUT $" + payable;
    InitialCount += 1;
  }
};

var checkout = async () => {
  document.getElementById("2").innerHTML =
    "<span class='loader-16' style='margin-left: 44%;'></span>";
  var payable = 0;
  url = "http://127.0.0.1:5000/products";

  try {
    let res = await axios.get(url);
    responseText = await res.data;
    products = responseText.products;

    for (let product of products) {
      payable = payable + parseFloat(product.payable);
    }

    // Updated payment url
    var paymentUrl = "/img/myqr.jpeg";

    await fetch(paymentUrl)
      .then(function (data) {
        return data.blob();
      })
      .then(function (img) {
        var image = URL.createObjectURL(img);
        $("#home").css("display", "none");
        $("#final").css("display", "none");
        window.scroll({
          top: 0,
          left: 0,
          behavior: "smooth",
        });
        $("#image").attr("src", image);
        $("#qr").css("display", "grid");
      });

    setTimeout(function () {
      $("#qr").css("display", "none");
      $("#success").css("display", "grid");
    }, 10000);

    setTimeout(function () {
      deleteProducts();
    }, 18000);
  } catch (error) {
    console.error("Error during checkout:", error);
  }
};
