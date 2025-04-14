import os
from flask import Flask, render_template, request, redirect, url_for
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


DOCTORS = [
    {"name": "Иванов И.И.", "specialty": "Терапевт"},
    {"name": "Петров П.П.", "specialty": "Хирург"},
    {"name": "Сидоров С.С.", "specialty": "Кардиолог"},
]

SCHEDULE = {
    "Иванов И.И.": ["10:00", "11:00", "15:00"],
    "Петров П.П.": ["09:00", "14:00", "16:00"],
    "Сидоров С.С.": ["08:00", "12:00", "17:00"],
}

appointments = []


@app.route('/')
def index():
    return render_template("index.html", doctors=DOCTORS, schedule=SCHEDULE)


@app.route('/schedule')
def schedule():
    return render_template("schedule.html", schedule=SCHEDULE)


@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        doctor = request.form['doctor']
        time = request.form['time']
        appointments.append({"name": name, "email": email, "doctor": doctor, "time": time})

        msg = Mail(
            from_email="arciomwyszynskitt@outlook.com",
            to_emails=email,
            subject="Подтверждение записи на прием",
            plain_text_content=f"Здравствуйте, {name}!\n\nВы записаны на прием к врачу {doctor} на {time}."
        )

        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(msg)
            print(f"Email отправлен! Статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

        appointment_index = len(appointments) - 1
        return redirect(url_for('confirmation', name=name, doctor=doctor, time=time, appointment_index=appointment_index))

    return render_template("appointment.html", doctors=DOCTORS, schedule=SCHEDULE)


@app.route('/confirmation')
def confirmation():
    name = request.args.get('name')
    doctor = request.args.get('doctor')
    time = request.args.get('time')
    appointment_index = int(request.args.get('appointment_index'))
    return render_template("confirmation.html", name=name, doctor=doctor, time=time, appointment_index=appointment_index)


@app.route('/cancel_appointment/<int:index>', methods=['GET'])
def cancel_appointment(index):
    if 0 <= index < len(appointments):
        canceled_appointment = appointments.pop(index)
        msg = Mail(
            from_email="arciomwyszynskitt@outlook.com",
            to_emails=canceled_appointment['email'],
            subject="Отмена записи на прием",
            plain_text_content=f"Здравствуйте, {canceled_appointment['name']}!\n\nВаша запись на прием к врачу {canceled_appointment['doctor']} на {canceled_appointment['time']} была отменена."
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(msg)
            print(f"Email об отмене отправлен! Статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка при отправке письма: {e}")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
