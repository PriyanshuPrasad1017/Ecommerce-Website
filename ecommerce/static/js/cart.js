var updateBtns = document.getElementsByClassName('update-cart')
for(var i=0;i<updateBtns.length;i++)
{
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId: ', productId, 'action: ', action);
        console.log('USER: ', user)
        if(user == 'AnonymousUser')
        {
            addCookieItem(productId, action)
        }
        else 
        {
            updateUserOrder(productId, action)
        }
    })
}

function updateUserOrder(productId, action)
{
    console.log('User is logged in, sending data..')
    var url = '/update_item/' // this is where we want to send the data
    // using fetch to send data
    fetch(url, { // this tells what kind of data we want to send
        method : 'POST',
        headers : {
            'Content-Type' : 'application/json', // used for text content
            'X-CSRFToken' : csrftoken,
        },
        // converting data object into string
        body : JSON.stringify({'productId' : productId, 'action' : action}) // the data we are going to send to the backend
    })

    .then((response) => {
        return response.json()
    })

    .then((data) => {
        console.log('data :', data)
        location.reload()
    })
}

function addCookieItem(productId, action)
{
    console.log('User is not authenticated')
    console.log('Not logged in..')
    if(action == 'add')
    {
        if(cart[productId] == undefined) // cart is in header of main.html file. 
        {
            cart[productId] = {'quantity' : 1}
        }
        else
        {
            cart[productId]['quantity'] += 1
        }
    }
    if(action == 'remove')
    {
        cart[productId]['quantity'] -= 1
        if(cart[productId]['quantity'] <= 0)
        {
            console.log('Remove item')
            delete cart[productId]
        }
    }
    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/" // reseting cookie
    location.reload()
}

