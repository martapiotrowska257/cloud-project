"use client";

import { useState, useEffect } from "react";
import axios from "axios";

type Task = {
  id: number;
  title: string;
  done: boolean;
};

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    async function fetchTasks() {
      try {
        const res = await axios.get("http://localhost:5000/tasks");
        setTasks(res.data);
      } catch (err) {
        console.error("Błąd pobierania zadań:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchTasks();
  }, []);

  // ── DODAJ ZADANIE ────────────────────────────────────────────────
  async function addTask() {
    if (!input.trim()) return; // nie dodawaj pustych zadań
    try {
      const res = await axios.post("http://localhost:5000/tasks", {
        title: input,
      });
      setTasks([res.data, ...tasks]); // dodaj na początek listy
      setInput("");
    } catch (err) {
      console.error("Błąd dodawania:", err);
    }
  }

  // ── TOGGLE DONE ──────────────────────────────────────────────────
  async function toggleTask(task: Task) {
    try {
      const res = await axios.put(`http://localhost:5000/tasks/${task.id}`, {
        done: !task.done, // odwróć obecny stan
      });
      setTasks(tasks.map((t) => (t.id === task.id ? res.data : t)));
    } catch (err) {
      console.error("Błąd aktualizacji:", err);
    }
  }

  // ── USUŃ ZADANIE ─────────────────────────────────────────────────
  async function deleteTask(id: number) {
    try {
      await axios.delete(`http://localhost:5000/tasks/${id}`);
      setTasks(tasks.filter((t) => t.id !== id)); // usuń z listy lokalnie
    } catch (err) {
      console.error("Błąd usuwania:", err);
    }
  }

  // ── ENTER W POLU TEKSTOWYM ───────────────────────────────────────
  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") addTask();
  }

  // ── WIDOK ────────────────────────────────────────────────────────
  return (
    <main className="container">
      <h1 className="title">moje zadania</h1>

      {/* Pole dodawania */}
      <div className="input-row">
        <input
          className="input"
          type="text"
          placeholder="nowe zadanie..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button className="btn-add" onClick={addTask}>
          dodaj
        </button>
      </div>

      {/* Lista zadań */}
      {loading ? (
        <p className="empty">ładowanie...</p>
      ) : tasks.length === 0 ? (
        <p className="empty">brak zadań — dodaj pierwsze! 🌸</p>
      ) : (
        <ul className="task-list">
          {tasks.map((task) => (
            <li
              key={task.id}
              className={`task-item ${task.done ? "done" : ""}`}
            >
              <button
                className="checkbox"
                onClick={() => toggleTask(task)}
                aria-label="oznacz jako ukończone"
              >
                {task.done ? "✓" : ""}
              </button>
              <span className="task-title">{task.title}</span>
              <button
                className="btn-delete"
                onClick={() => deleteTask(task.id)}
                aria-label="usuń zadanie"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
