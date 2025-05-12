let currentState = {
    from: 'Москва',
    to: 'Санкт-Петербург',
    date: '2023-12-15',
    selectedTrain: null,
    selectedSeat: null,
    passengerInfo: null,
    orders: []
};

document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    document.getElementById('date').value = dateStr;
    currentState.date = dateStr;
});

function searchTrains() {
    currentState.from = document.getElementById('from').value;
    currentState.to = document.getElementById('to').value;
    currentState.date = document.getElementById('date').value;
    
    document.getElementById('search-title').textContent = 
        `${currentState.from} → ${currentState.to}, ${formatDate(currentState.date)}`;
    
    showPage('results');
}

function selectTrain(trainId) {
    currentState.selectedTrain = trainId;
    
    document.getElementById('train-date').textContent = formatDate(currentState.date);
    
    showPage('seats');
}

function selectSeat(seatElement) {
    document.querySelectorAll('.seat').forEach(s => s.classList.remove('selected'));
    
    if (!seatElement.classList.contains('booked')) {
        seatElement.classList.add('selected');
        currentState.selectedSeat = seatElement.innerText;
        
        document.getElementById('order-seat').textContent = `Место: ${currentState.selectedSeat}, вагон 5`;
    }
}

function proceedToCheckout() {
    if (!currentState.selectedSeat) {
        alert('Пожалуйста, выберите место');
        return;
    }
    
    const trainInfo = currentState.selectedTrain === 1 ? 
        'Поезд №753' : 'Электричка №17';
    const price = currentState.selectedTrain === 1 ? '30' : '22';
    
    document.getElementById('order-train').textContent = 
        `${trainInfo}, ${formatDate(currentState.date)}, ${currentState.selectedTrain === 1 ? '07:00' : '12:30'}`;
    document.getElementById('order-price').textContent = price;
    
    showPage('checkout');
}

function confirmOrder() {
    const lastname = document.getElementById('lastname').value;
    const firstname = document.getElementById('firstname').value;
    
    if (!lastname || !firstname) {
        alert('Пожалуйста, заполните обязательные поля (Фамилия и Имя)');
        return;
    }
    
    currentState.passengerInfo = {
        lastname: lastname,
        firstname: document.getElementById('firstname').value,
        middlename: document.getElementById('middlename').value,
        passport: document.getElementById('passport').value
    };
    
    const trainInfo = currentState.selectedTrain === 1 ? 
        'Поезд №753' : 'Электричка №17';
    const price = currentState.selectedTrain === 1 ? 2500 : 1800;
    
    const order = {
        id: Date.now(),
        train: trainInfo,
        trainId: currentState.selectedTrain,
        seat: currentState.selectedSeat,
        date: currentState.date,
        from: currentState.from,
        to: currentState.to,
        departureTime: currentState.selectedTrain === 1 ? '07:00' : '12:30',
        arrivalTime: currentState.selectedTrain === 1 ? '11:30' : '17:45',
        passenger: currentState.passengerInfo,
        price: price,
        status: 'active'
    };
    
    currentState.orders.push(order);
    
    document.getElementById('order-id').textContent = order.id;
    
    showPage('success');
    
    updateTripList();
}

function showTicket(orderId) {
    const order = currentState.orders.find(o => o.id == orderId);
    if (order) {
        alert(`Билет №${order.id}\n` +
              `${order.train}\n` +
              `${order.from} → ${order.to}\n` +
              `${formatDate(order.date)} ${order.departureTime}-${order.arrivalTime}\n` +
              `Место ${order.seat}, вагон 5\n` +
              `Пассажир: ${order.passenger.lastname} ${order.passenger.firstname}\n` +
              `Стоимость: ${order.price} ₽`);
    }
}

function returnTicket(orderId) {
    if (confirm('Вы уверены, что хотите вернуть билет?')) {
        const orderIndex = currentState.orders.findIndex(o => o.id == orderId);
        if (orderIndex !== -1) {
            currentState.orders[orderIndex].status = 'returned';
            alert('Билет возвращен');
            updateTripList();
        }
    }
}

function updateTripList() {
    const tripList = document.getElementById('trip-list');
    const noTrips = document.getElementById('no-trips');
    
    if (currentState.orders.length > 0) {
        noTrips.style.display = 'none';
        tripList.style.display = 'block';
        tripList.innerHTML = '';
        
        currentState.orders.forEach(order => {
            const tripCard = document.createElement('div');
            tripCard.className = 'trip-card';
            tripCard.innerHTML = `
                <p><strong>${order.train}</strong></p>
                <p>${order.from} → ${order.to}</p>
                <p>${formatDate(order.date)} ${order.departureTime}-${order.arrivalTime}</p>
                <p>Место ${order.seat}, вагон 5</p>
                <p>Статус: ${order.status === 'active' ? 'Активен' : 'Возвращен'}</p>
                <button onclick="showTicket(${order.id})">Показать билет</button>
                ${order.status === 'active' ? 
                    `<button onclick="returnTicket(${order.id})">Вернуть билет</button>` : ''}
            `;
            tripList.appendChild(tripCard);
        });
    } else {
        noTrips.style.display = 'block';
        tripList.style.display = 'none';
    }
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(pageId).style.display = 'block';
    
    if (pageId === 'account') {
        updateTripList();
    }
}

function formatDate(dateStr) {
    const months = [
        'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
        'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'
    ];
    
    const date = new Date(dateStr);
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    
    return `${day} ${month} ${year} года`;
}