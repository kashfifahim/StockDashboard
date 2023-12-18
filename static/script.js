function fetchStocks() {
    fetch('/stocks')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('stocks-container');
            container.innerHTML = '';
            data.stocks.forEach(stock => {
                const stockDiv = document.createElement('div');
                stockDiv.innerHTML = `Symbol: ${stock.symbol}, Share: ${stock.share}, Price: ${stock.price}`;
                container.appendChild(stockDiv);
            });
        })
        .catch(error => console.error('Error', error));
}

window.onload = fetchStocks;