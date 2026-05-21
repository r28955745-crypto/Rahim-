import matplotlib.pyplot as plt
import io
import db_handler

def generate_mood_graph(user_id):
    history = db_handler.get_history(user_id)
    
    if not history:
        return None

    dates = []
    moods = []
    studies = []
    sleeps = []

    for record in history:
        dates.append(record['date'])
        moods.append(record['mood'])
        studies.append(record['study'])
        sleeps.append(record['sleep'])

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color = 'tab:red'
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Настроение (1-5)', color=color)
    ax1.plot(dates, moods, color=color, marker='o', label='Настроение')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim(0, 6)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.set_ylabel('Часы (Учеба/Сон)', color=color)
    ax2.plot(dates, studies, color='tab:green', marker='s', linestyle='--', label='Учеба')
    ax2.plot(dates, sleeps, color='tab:orange', marker='^', linestyle=':', label='Сон')
    ax2.tick_params(axis='y', labelcolor=color)
    
    max_val = max(max(studies), max(sleeps)) if studies and sleeps else 10
    ax2.set_ylim(0, max_val + 2)

    fig.tight_layout()
    plt.title(f"Трекер настроения и продуктивности")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

    return buf