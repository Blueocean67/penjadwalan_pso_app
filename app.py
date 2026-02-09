from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import sqlite3, pandas as pd, numpy as np, os, json, random, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

app = Flask(__name__)
app.secret_key = 'secret123'
DB = 'data.db'

os.makedirs('static', exist_ok=True)

# ================= DATABASE =================

def run_query(sql, params=(), fetch=False):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql, params)
    if fetch:
        rows = cur.fetchall()
        conn.close()
        return rows
    conn.commit()
    conn.close()

def load_df(table):
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

def get_primary_key(table):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    conn.close()
    for c in cols:
        if c[5] == 1:
            return c[1]
    return cols[0][1]

# ================= TASK =================

def build_tasks():
    mapel_df = load_df('mapel')
    kelas_df = load_df('kelas')
    tasks = []
    for _, k in kelas_df.iterrows():
        for _, m in mapel_df.iterrows():
            for _ in range(int(m['jam_per_minggu'])):
                tasks.append({'kelas': k['id_kelas'], 'mapel': m['id_mapel']})
    return tasks

# ================= FITNESS =================

def evaluate_schedule(chrom, tasks, guru_df, slot_count):
    penalty = 0
    guru_slot = {}
    class_slot = {}
    guru_mapel = {int(r['id']): int(r['mapel_id']) for _, r in guru_df.iterrows()}

    for i, (gid, sidx) in enumerate(chrom):
        t = tasks[i]

        if guru_mapel[gid] != t['mapel']:
            penalty += 5

        if (gid, sidx) in guru_slot:
            penalty += 10
        guru_slot[(gid, sidx)] = 1

        if (t['kelas'], sidx) in class_slot:
            penalty += 15
        class_slot[(t['kelas'], sidx)] = 1

    return 1 / (1 + penalty), penalty

# ================= GA =================

def random_chrom(tasks, slot_count, guru_ids):
    return [(random.choice(guru_ids), random.randrange(slot_count)) for _ in tasks]

def ga(tasks, guru_df, slot_count, pop=50, gen=100, mut=0.05):
    guru_ids = list(guru_df['id'])
    population = [random_chrom(tasks, slot_count, guru_ids) for _ in range(pop)]
    best, best_fit = None, -1
    history = []

    for _ in range(gen):
        fits = []
        for ind in population:
            f, _ = evaluate_schedule(ind, tasks, guru_df, slot_count)
            fits.append(f)
            if f > best_fit:
                best_fit, best = f, ind.copy()
        history.append(best_fit)

        new_pop = [best.copy()]
        while len(new_pop) < pop:
            a, b = random.sample(range(pop), 2)
            p1, p2 = population[a], population[b]
            cut = random.randint(1, len(p1) - 1)
            c = p1[:cut] + p2[cut:]
            if random.random() < mut:
                i = random.randrange(len(c))
                c[i] = (random.choice(guru_ids), random.randrange(slot_count))
            new_pop.append(c)
        population = new_pop

    return best, best_fit, history



# ================= RESULT =================

def chrom_to_per_kelas(chrom, tasks):
    slot = load_df('slot_waktu')
    mapel = load_df('mapel')
    guru = load_df('guru')
    kelas = load_df('kelas')

    hasil = {}
    for i, (gid, sidx) in enumerate(chrom):
        t = tasks[i]
        nama_kelas = kelas.loc[kelas.id_kelas == t['kelas'], 'nama_kelas'].values[0]
        row = {
            'Hari': slot.iloc[sidx]['hari'],
            'Jam': slot.iloc[sidx]['jam_ke'],
            'Mapel': mapel.loc[mapel.id_mapel == t['mapel'], 'nama_mapel'].values[0],
            'Guru': guru.loc[guru.id == gid, 'nama_guru'].values[0]
        }
        hasil.setdefault(nama_kelas, []).append(row)

    return hasil

def generate_pdf_per_kelas(data):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Jadwal Per Kelas", styles['Title']), Spacer(1, 12)]

    for k, rows in data.items():
        df = pd.DataFrame(rows)
        story.append(Paragraph(f"Kelas {k}", styles['Heading2']))
        tbl = Table([df.columns.tolist()] + df.values.tolist())
        tbl.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.5,colors.grey),
            ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)
        ]))
        story.append(tbl)
        story.append(Spacer(1, 20))

    doc.build(story)
    buf.seek(0)
    return buf

# ================= AUTH =================

@app.route('/')
def root():
    return redirect(url_for('dashboard')) if 'user' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        if run_query("SELECT * FROM users WHERE username=? AND password=?", (u,p), True):
            session['user'] = u
            return redirect(url_for('dashboard'))
        flash('Login gagal')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ================= DASHBOARD & DATA =================

@app.route('/dashboard')
def dashboard():
    return render_template(
        'dashboard.html',
        g=len(load_df('guru')),
        m=len(load_df('mapel')),
        k=len(load_df('kelas')),
        s=len(load_df('slot_waktu'))
    )

@app.route('/data/<table>', methods=['GET','POST'])
def data(table):
    df = load_df(table)
    pk = get_primary_key(table)

    if request.method == 'POST':
        form = dict(request.form)
        cols = ','.join(form.keys())
        qs = ','.join('?' for _ in form)
        run_query(f"INSERT INTO {table} ({cols}) VALUES ({qs})", tuple(form.values()))
        return redirect(url_for('data', table=table))

    return render_template('data_table.html',
        table=table,
        data=df.to_dict(orient='records'),
        cols=df.columns,
        pk=pk
    )
@app.route('/delete/<table>/<row_id>', methods=['POST'])
def delete_row(table, row_id):
    pk = get_primary_key(table)
    run_query(f"DELETE FROM {table} WHERE {pk} = ?", (row_id,))
    return redirect(url_for('data', table=table))

# ================= RUN =================

@app.route('/run', methods=['GET','POST'])
def run_opt():
    if request.method == 'POST':
        tasks = build_tasks()
        guru = load_df('guru')
        slot_count = len(load_df('slot_waktu'))

        # Jalankan GA
        best, fit, hist = ga(tasks, guru, slot_count)

        # Simpan hasil GA untuk PDF
        with open('best_schedule.json','w') as f:
            json.dump(best, f)

        # Buat grafik fitness history
        plt.figure(figsize=(8,4))
        plt.plot(hist, marker='o', color='blue')
        plt.title("Perkembangan Fitness Terbaik per Generasi")
        plt.xlabel("Generasi")
        plt.ylabel("Fitness")
        plt.grid(True)
        os.makedirs('static', exist_ok=True)
        plt.savefig(os.path.join('static', 'fitness_chart.png'))
        plt.close()

        # Hasil jadwal per kelas
        jadwal = chrom_to_per_kelas(best, tasks)
        return render_template('result.html', jadwal=jadwal, fit=fit)

    return render_template('run_page.html')


@app.route('/download_pdf_per_kelas')
def download_pdf():
    with open('best_schedule.json') as f:
        chrom = json.load(f)
    tasks = build_tasks()
    pdf = generate_pdf_per_kelas(chrom_to_per_kelas(chrom, tasks))
    return send_file(pdf, as_attachment=True, download_name='jadwal_per_kelas.pdf')

# ================= RUN APP =================

if __name__ == '__main__':
    app.run(debug=True)
