import React, { useMemo, useState } from "react";

const userProfile = {
  name: "Daniel Mabalot",
  firstName: "Daniel",
  initials: "DM",
  email: "daniel.mabalot@busybee.app"
};

const initialTasks = [
  {
    id: "weekly-report",
    title: "Prepare weekly report",
    project: "Work",
    projectTone: "blue",
    priority: "High",
    priorityTone: "amber",
    due: "Today, 10:00 AM",
    group: "Focus",
    completed: false,
    selected: true,
    notes:
      "Compile key updates, performance metrics, and upcoming priorities for the weekly stakeholder update.",
    subtasks: [
      { label: "Gather analytics highlights", done: true },
      { label: "Write executive summary", done: false },
      { label: "Attach final screenshots", done: false }
    ],
    status: "In Progress",
    estimate: "2h 30m",
    assignee: userProfile.name
  },
  {
    id: "invoice-notes",
    title: "Review invoice notes",
    project: "Work",
    projectTone: "blue",
    priority: "Medium",
    priorityTone: "yellow",
    due: "Today, 1:00 PM",
    group: "Focus",
    completed: false,
    notes: "Confirm line items before the finance sync.",
    subtasks: [
      { label: "Compare final bill", done: false },
      { label: "Flag vendor questions", done: false }
    ],
    status: "Not Started",
    estimate: "35m",
    assignee: userProfile.name
  },
  {
    id: "team-sync",
    title: "Book team sync",
    project: "Work",
    projectTone: "blue",
    priority: "Low",
    priorityTone: "green",
    due: "Today, 3:30 PM",
    group: "Focus",
    completed: false,
    notes: "Find a 30 minute slot for design QA handoff.",
    subtasks: [{ label: "Check manager availability", done: false }],
    status: "Not Started",
    estimate: "10m",
    assignee: userProfile.name
  },
  {
    id: "project-recap",
    title: "Send project recap",
    project: "Marketing",
    projectTone: "violet",
    priority: "Medium",
    priorityTone: "yellow",
    due: "Today, 5:00 PM",
    group: "Later Today",
    completed: false,
    notes: "Summarize decisions, blockers, and next milestones.",
    subtasks: [{ label: "Draft recap", done: false }],
    status: "Queued",
    estimate: "25m",
    assignee: userProfile.name
  },
  {
    id: "moodboard",
    title: "Finalize moodboard",
    project: "Design",
    projectTone: "orange",
    priority: "Low",
    priorityTone: "green",
    due: "Today, 6:30 PM",
    group: "Later Today",
    completed: false,
    notes: "Tighten visual references and export the final board.",
    subtasks: [
      { label: "Remove weak references", done: true },
      { label: "Add mobile direction", done: false }
    ],
    status: "Queued",
    estimate: "45m",
    assignee: userProfile.name
  },
  {
    id: "website-hero",
    title: "Update website hero section",
    project: "Marketing",
    projectTone: "violet",
    priority: "Medium",
    priorityTone: "yellow",
    due: "Today, 9:00 AM",
    group: "Done",
    completed: true,
    notes: "Hero polish complete and ready for QA.",
    subtasks: [{ label: "Publish final copy", done: true }],
    status: "Done",
    estimate: "1h",
    assignee: userProfile.name
  },
  {
    id: "client-feedback",
    title: "Reply to client email",
    project: "Work",
    projectTone: "blue",
    priority: "High",
    priorityTone: "amber",
    due: "Yesterday",
    group: "Done",
    completed: true,
    notes: "Answered and archived.",
    subtasks: [{ label: "Send response", done: true }],
    status: "Done",
    estimate: "15m",
    assignee: userProfile.name
  },
  {
    id: "organize-files",
    title: "Organize design assets",
    project: "Design",
    projectTone: "orange",
    priority: "Low",
    priorityTone: "green",
    due: "Today, 12:15 PM",
    group: "Done",
    completed: true,
    notes: "Components and source assets cleaned up.",
    subtasks: [{ label: "Rename layers", done: true }],
    status: "Done",
    estimate: "20m",
    assignee: userProfile.name
  }
];

const navItems = [
  ["sun", "Today", ""],
  ["inbox", "Inbox", "2"],
  ["calendar", "Upcoming", ""],
  ["calendarDays", "Calendar", ""],
  ["user", "My Tasks", ""]
];

const projects = [
  ["Work", "blue", 12],
  ["Marketing", "violet", 7],
  ["Design", "orange", 5],
  ["Personal", "green", 4],
  ["Finance", "teal", 3]
];

const tokens = [
  ["Background", "#F8F7F3"],
  ["Surface", "#FFFFFF"],
  ["Ink", "#162237"],
  ["Muted", "#697386"],
  ["Honey", "#F5A300"],
  ["Success", "#2FAE66"],
  ["Border", "#E7E0D6"],
  ["Focus", "#FFF6E1"]
];

function Icon({ name, size = 18, className = "" }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: "1.9",
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
    className: `icon ${className}`
  };

  const paths = {
    plus: <path d="M12 5v14M5 12h14" />,
    search: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="m20 20-3.2-3.2" />
      </>
    ),
    more: <path d="M5 12h.01M12 12h.01M19 12h.01" />,
    sun: (
      <>
        <circle cx="12" cy="12" r="3.5" />
        <path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4" />
      </>
    ),
    inbox: (
      <>
        <path d="M4 5h16l2 9v5H2v-5l2-9Z" />
        <path d="M2 14h6l1.5 2h5L16 14h6" />
      </>
    ),
    calendar: (
      <>
        <path d="M7 3v4M17 3v4" />
        <rect x="3.5" y="5" width="17" height="15.5" rx="2.5" />
        <path d="M3.5 10h17" />
      </>
    ),
    calendarDays: (
      <>
        <path d="M8 3v4M16 3v4" />
        <rect x="3.5" y="5" width="17" height="15.5" rx="2.5" />
        <path d="M3.5 10h17M8 14h.01M12 14h.01M16 14h.01M8 17h.01M12 17h.01" />
      </>
    ),
    user: (
      <>
        <circle cx="12" cy="8" r="3.4" />
        <path d="M5 20c1.2-3.5 4-5.2 7-5.2s5.8 1.7 7 5.2" />
      </>
    ),
    target: (
      <>
        <circle cx="12" cy="12" r="7.5" />
        <circle cx="12" cy="12" r="3" />
        <path d="M14.5 9.5 20 4" />
      </>
    ),
    clock: (
      <>
        <circle cx="12" cy="12" r="8.5" />
        <path d="M12 7.5V12l3 2" />
      </>
    ),
    check: <path d="m5 12 4 4 10-10" />,
    chevron: <path d="m8 10 4 4 4-4" />,
    flag: (
      <>
        <path d="M6 20V5" />
        <path d="M6 5c4-2 6 2 10 0v9c-4 2-6-2-10 0" />
      </>
    ),
    star: (
      <path d="m12 3 2.7 5.5 6 .9-4.3 4.2 1 5.9L12 16.7l-5.4 2.8 1-5.9-4.3-4.2 6-.9L12 3Z" />
    ),
    bell: (
      <>
        <path d="M18 9.5a6 6 0 0 0-12 0c0 7-2.5 6-2.5 8h17c0-2-2.5-1-2.5-8Z" />
        <path d="M10 20a2.2 2.2 0 0 0 4 0" />
      </>
    ),
    tag: (
      <>
        <path d="M20 13 13 20 4 11V4h7l9 9Z" />
        <circle cx="8" cy="8" r="1" />
      </>
    ),
    layers: (
      <>
        <path d="m12 3 8 4-8 4-8-4 8-4Z" />
        <path d="m4 12 8 4 8-4M4 17l8 4 8-4" />
      </>
    ),
    send: (
      <>
        <path d="M21 3 10 14" />
        <path d="m21 3-7 18-4-7-7-4 18-7Z" />
      </>
    ),
    filter: <path d="M4 6h16M7 12h10M10 18h4" />,
    note: (
      <>
        <path d="M6 4h12v16H6z" />
        <path d="M9 8h6M9 12h6M9 16h4" />
      </>
    ),
    spark: (
      <>
        <path d="M12 3v5M12 16v5M3 12h5M16 12h5" />
        <path d="m5.5 5.5 3.2 3.2M15.3 15.3l3.2 3.2M18.5 5.5l-3.2 3.2M8.7 15.3l-3.2 3.2" />
      </>
    )
  };

  return <svg {...common}>{paths[name] || paths.note}</svg>;
}

function Dot({ tone = "blue" }) {
  return <span className={`dot dot-${tone}`} aria-hidden="true" />;
}

function BrandWordmark() {
  return (
    <div className="type-logo" aria-label="BusyBee">
      <span>Busy</span>
      <span>Bee</span>
      <i aria-hidden="true" />
    </div>
  );
}

function Chip({ icon, tone = "neutral", children }) {
  return (
    <span className={`chip chip-${tone}`}>
      {icon ? <Icon name={icon} size={13} /> : null}
      {children}
    </span>
  );
}

function TaskCheck({ checked, onClick, label }) {
  return (
    <button
      type="button"
      className={`task-check ${checked ? "checked" : ""}`}
      onClick={onClick}
      aria-label={label}
    >
      {checked ? <Icon name="check" size={14} /> : null}
    </button>
  );
}

function TaskRow({ task, selected, onSelect, onToggle, compact = false }) {
  return (
    <article
      className={`task-row ${task.completed ? "is-complete" : ""} ${
        selected ? "is-selected" : ""
      } ${compact ? "compact" : ""}`}
      onClick={() => onSelect(task.id)}
    >
      <span className="drag-dots" aria-hidden="true">
        <i />
        <i />
        <i />
        <i />
        <i />
        <i />
      </span>
      <TaskCheck
        checked={task.completed}
        onClick={(event) => {
          event.stopPropagation();
          onToggle(task.id);
        }}
        label={`${task.completed ? "Reopen" : "Complete"} ${task.title}`}
      />
      <div className="task-copy">
        <h4>{task.title}</h4>
        <div className="task-meta">
          <Chip tone={task.projectTone}>
            <Dot tone={task.projectTone} />
            {task.project}
          </Chip>
          {!compact ? (
            <>
              <Chip tone={task.priorityTone} icon="flag">
                {task.priority}
              </Chip>
              <Chip tone="neutral" icon="calendar">
                {task.due}
              </Chip>
            </>
          ) : (
            <span className="mobile-time">{task.due.replace("Today, ", "")}</span>
          )}
        </div>
      </div>
      <button className="star-button" type="button" aria-label="Favorite task">
        <Icon name="star" size={19} />
      </button>
    </article>
  );
}

function SectionHeader({ icon, title, count, progress }) {
  return (
    <div className="section-header">
      <div>
        <Icon name={icon} />
        <h3>{title}</h3>
      </div>
      <div className="section-tools">
        {progress ? (
          <span className="mini-progress">
            <span>{progress.label}</span>
            <i>
              <b style={{ width: progress.width }} />
            </i>
          </span>
        ) : (
          <span>{count}</span>
        )}
        <Icon name="chevron" size={16} />
      </div>
    </div>
  );
}

function DesktopScreen({ tasks, selectedId, setSelectedId, toggleTask, createTask }) {
  const [filter, setFilter] = useState("All");
  const [draft, setDraft] = useState("");

  const visibleTasks = tasks.filter((task) => {
    if (filter === "Active") return !task.completed;
    if (filter === "Completed") return task.completed;
    return true;
  });

  const groups = {
    Focus: visibleTasks.filter((task) => task.group === "Focus" && !task.completed),
    "Later Today": visibleTasks.filter(
      (task) => task.group === "Later Today" && !task.completed
    ),
    Done: visibleTasks.filter((task) => task.completed)
  };

  const selectedTask =
    tasks.find((task) => task.id === selectedId) ||
    tasks.find((task) => !task.completed) ||
    tasks[0];

  const completed = tasks.filter((task) => task.completed).length;

  function submitDraft(event) {
    event.preventDefault();
    if (!draft.trim()) return;
    const id = createTask(draft.trim());
    setSelectedId(id);
    setDraft("");
  }

  return (
    <section className="screen-block" id="desktop">
      <FrameLabel
        kicker="Required desktop screen"
        title="Desktop / Today Dashboard"
        description="Three-column task cockpit with pending work, completed work, and selected task details."
      />
      <div className="desktop-frame" data-testid="desktop-frame">
        <aside className="sidebar">
          <BrandWordmark />
          <button className="new-task-button" type="button">
            <Icon name="plus" />
            New Task
          </button>
          <nav aria-label="Primary">
            {navItems.map(([icon, label, badge], index) => (
              <button className={index === 0 ? "active" : ""} type="button" key={label}>
                <Icon name={icon} />
                <span>{label}</span>
                {badge ? <em>{badge}</em> : null}
              </button>
            ))}
          </nav>
          <div className="sidebar-title">
            <span>Projects</span>
            <Icon name="plus" size={16} />
          </div>
          <div className="project-list">
            {projects.map(([name, tone, count]) => (
              <button type="button" key={name}>
                <Dot tone={tone} />
                <span>{name}</span>
                <em>{count}</em>
              </button>
            ))}
          </div>
          <div className="sidebar-lower">
            <button type="button">
              <Icon name="tag" />
              Tags
            </button>
            <button type="button">
              <Icon name="filter" />
              Filters
            </button>
          </div>
          <div className="profile-card">
            <span>{userProfile.initials}</span>
            <div>
              <strong>{userProfile.name}</strong>
              <small>{userProfile.email}</small>
            </div>
          </div>
        </aside>

        <main className="task-pane">
          <header className="task-pane-header">
            <div>
              <h2>Today</h2>
              <p>
                {tasks.length} tasks <i /> {completed} completed
              </p>
            </div>
            <div className="header-actions">
              <button type="button" aria-label="Search">
                <Icon name="search" />
              </button>
              <button type="button" aria-label="Filter">
                <Icon name="filter" />
              </button>
              <button type="button" aria-label="More">
                <Icon name="more" />
              </button>
            </div>
          </header>

          <form className="quick-add" onSubmit={submitDraft}>
            <Icon name="plus" />
            <input
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") submitDraft(event);
              }}
              placeholder="Add a task, then press Enter"
              aria-label="Add a new task"
            />
            <button type="submit">Add</button>
          </form>

          <div className="segmented-control" role="tablist" aria-label="Task filter">
            {["All", "Active", "Completed"].map((item) => (
              <button
                className={filter === item ? "selected" : ""}
                type="button"
                key={item}
                onClick={() => setFilter(item)}
              >
                {item}
              </button>
            ))}
          </div>

          <div className="task-groups">
            <SectionHeader
              icon="target"
              title="Focus"
              progress={{ label: "2 of 3", width: "64%" }}
            />
            <div className="rows">
              {groups.Focus.map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  selected={task.id === selectedId}
                  onSelect={setSelectedId}
                  onToggle={toggleTask}
                />
              ))}
            </div>

            <SectionHeader
              icon="clock"
              title="Later Today"
              count={`${groups["Later Today"].length} tasks`}
            />
            <div className="rows">
              {groups["Later Today"].map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  selected={task.id === selectedId}
                  onSelect={setSelectedId}
                  onToggle={toggleTask}
                />
              ))}
            </div>

            <SectionHeader icon="check" title="Done" count={`${groups.Done.length} tasks`} />
            <div className="rows done-rows">
              {groups.Done.map((task) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  selected={task.id === selectedId}
                  onSelect={setSelectedId}
                  onToggle={toggleTask}
                />
              ))}
            </div>
          </div>
        </main>

        <TaskDetail task={selectedTask} toggleTask={toggleTask} />
      </div>
    </section>
  );
}

function TaskDetail({ task, toggleTask }) {
  return (
    <aside className="detail-panel" data-testid="detail-panel">
      <div className="detail-topline">
        <TaskCheck
          checked={task.completed}
          onClick={() => toggleTask(task.id)}
          label={`${task.completed ? "Reopen" : "Complete"} selected task`}
        />
        <Chip tone="amber" icon="flag">
          {task.priority} Priority
        </Chip>
        <button type="button" aria-label="Close detail">
          x
        </button>
      </div>
      <h2>{task.title}</h2>
      <div className="detail-chips">
        <Chip tone={task.projectTone}>
          <Dot tone={task.projectTone} />
          {task.project}
        </Chip>
        <Chip tone="neutral" icon="calendar">
          {task.due}
        </Chip>
        <Chip tone="neutral" icon="bell">
          10 min before
        </Chip>
      </div>
      <div className="detail-tabs" role="tablist" aria-label="Task detail tabs">
        <button type="button" className="selected">
          Detail
        </button>
        <button type="button">
          Subtasks <span>{task.subtasks.length}</span>
        </button>
        <button type="button">Notes</button>
      </div>
      <p className="detail-note">{task.notes}</p>
      <div className="detail-fields">
        <DetailField icon="check" label="Status" value={task.status} tone="yellow" />
        <DetailField icon="user" label="Assignee" value={task.assignee} />
        <DetailField icon="calendar" label="Due date" value="Today, May 7" />
        <DetailField icon="clock" label="Time estimate" value={task.estimate} />
        <DetailField icon="tag" label="Tags" value="Report, Weekly" />
      </div>
      <div className="subtask-card">
        <h3>Subtasks</h3>
        {task.subtasks.map((subtask) => (
          <label key={subtask.label}>
            <span className={subtask.done ? "subtask-check done" : "subtask-check"}>
              {subtask.done ? <Icon name="check" size={12} /> : null}
            </span>
            {subtask.label}
          </label>
        ))}
      </div>
      <div className="activity-list">
        <h3>Activity</h3>
        <p>
          <span>{userProfile.initials}</span>
          <span className="activity-copy">
            You created this task
            <small>May 7, 9:15 AM</small>
          </span>
        </p>
        <p>
          <span>{userProfile.initials}</span>
          <span className="activity-copy">
            You set priority to <strong>{task.priority}</strong>
            <small>May 7, 9:16 AM</small>
          </span>
        </p>
      </div>
      <label className="comment-box">
        <span>{userProfile.initials}</span>
        <input placeholder="Add a comment..." />
        <Icon name="send" />
      </label>
    </aside>
  );
}

function DetailField({ icon, label, value, tone }) {
  return (
    <div>
      <Icon name={icon} />
      <span>{label}</span>
      <strong className={tone ? `field-${tone}` : ""}>{value}</strong>
    </div>
  );
}

function PhoneFrame({ tasks, toggleTask, createTask }) {
  const [tab, setTab] = useState("Today");
  const [sheetOpen, setSheetOpen] = useState(false);
  const [toast, setToast] = useState(true);
  const [draft, setDraft] = useState("Plan tomorrow sprint");

  const activeTasks = tasks.filter((task) => !task.completed).slice(0, 3);
  const doneTasks = tasks.filter((task) => task.completed).slice(0, 3);

  function completeTask(id) {
    toggleTask(id);
    setToast(true);
  }

  function saveTask() {
    if (draft.trim()) createTask(draft.trim());
    setSheetOpen(false);
    setToast(true);
  }

  return (
    <section className="screen-block" id="mobile">
      <FrameLabel
        kicker="Required mobile screen + bonus state"
        title="Mobile / Today List and Edit Sheet"
        description="Thumb-friendly task flow with completion feedback and a bottom-sheet editor state."
      />
      <div className="mobile-board">
        <div className="phone-shell" data-testid="mobile-list">
          <div className="phone-status">
            <span>9:41</span>
            <span>|||</span>
          </div>
          <header className="mobile-header">
            <BrandWordmark />
            <div>
              <button type="button" aria-label="Search">
                <Icon name="search" />
              </button>
              <button type="button" aria-label="More">
                <Icon name="more" />
              </button>
            </div>
          </header>
          <p className="mobile-greeting">Good morning, {userProfile.firstName}</p>
          <div className="mobile-title-row">
            <h2>Today</h2>
            <span>
              <Icon name="sun" />
              Tue, May 6
            </span>
          </div>
          <div className="mobile-progress">
            <div className="progress-ring">
              <span>3/6</span>
            </div>
            <div>
              <strong>6 tasks</strong>
              <small>total</small>
            </div>
            <div>
              <strong className="success-text">3 completed</strong>
              <small>keep going!</small>
            </div>
          </div>
          <div className="mobile-tabs">
            {["Today", "Upcoming", "Done"].map((item) => (
              <button
                type="button"
                key={item}
                className={tab === item ? "active" : ""}
                onClick={() => setTab(item)}
              >
                {item}
              </button>
            ))}
          </div>
          <div className="mobile-section-title">
            <span>
              <Icon name={tab === "Done" ? "check" : "target"} />
              {tab === "Done" ? "Completed" : "Focus"}
            </span>
            <em>{tab === "Done" ? doneTasks.length : activeTasks.length}</em>
          </div>
          <div className="mobile-task-list">
            {(tab === "Done" ? doneTasks : activeTasks).map((task) => (
              <TaskRow
                compact
                key={`${tab}-${task.id}`}
                task={task}
                selected={false}
                onSelect={() => setSheetOpen(true)}
                onToggle={completeTask}
              />
            ))}
          </div>
          <button
            className="fab"
            type="button"
            aria-label="Open new task sheet"
            onClick={() => setSheetOpen(true)}
          >
            <Icon name="plus" size={28} />
          </button>
          <nav className="mobile-nav" aria-label="Mobile navigation">
            {[
              ["sun", "Today"],
              ["layers", "My Lists"],
              ["calendar", "Calendar"],
              ["user", "Profile"]
            ].map(([icon, label], index) => (
              <button type="button" className={index === 0 ? "active" : ""} key={label}>
                <Icon name={icon} />
                <span>{label}</span>
              </button>
            ))}
          </nav>
          {toast ? (
            <div className="mobile-toast" data-testid="mobile-toast">
              <span>
                <Icon name="check" />
              </span>
              <div>
                <strong>Task completed</strong>
                <small>Update website hero section</small>
              </div>
              <button type="button" onClick={() => setToast(false)}>
                Undo
              </button>
            </div>
          ) : null}
          {sheetOpen ? (
            <div className="sheet-backdrop">
              <MobileSheet
                draft={draft}
                setDraft={setDraft}
                onClose={() => setSheetOpen(false)}
                onSave={saveTask}
              />
            </div>
          ) : null}
        </div>

        <div className="phone-shell phone-editor" data-testid="mobile-editor">
          <div className="phone-status">
            <span>9:41</span>
            <span>|||</span>
          </div>
          <div className="dimmed-mobile-bg">
            <BrandWordmark />
            <p>Good morning, {userProfile.firstName}</p>
            <h2>Today</h2>
          </div>
          <MobileSheet
            draft="Prepare weekly report"
            setDraft={() => {}}
            onClose={() => {}}
            onSave={() => {}}
            fixed
          />
        </div>
      </div>
    </section>
  );
}

function MobileSheet({ draft, setDraft, onClose, onSave, fixed = false }) {
  return (
    <div className={`mobile-sheet ${fixed ? "fixed" : ""}`}>
      <span className="sheet-grip" />
      <div className="sheet-header">
        <button type="button" onClick={onClose} aria-label="Close sheet">
          x
        </button>
        <strong>New Task</strong>
        <button type="button" aria-label="Expand sheet">
          <Icon name="spark" />
        </button>
      </div>
      <label className="sheet-title">
        <TaskCheck checked={false} onClick={() => {}} label="Task not complete" />
        <input value={draft} onChange={(event) => setDraft(event.target.value)} />
      </label>
      <div className="sheet-card priority-picker">
        <div>
          <Icon name="flag" />
          <span>Priority</span>
        </div>
        <div className="priority-row">
          {[
            ["amber", "Urgent priority"],
            ["orange", "High priority"],
            ["yellow", "Medium priority"],
            ["blue", "Low priority"],
            ["neutral", "No priority"]
          ].map(([tone, label], index) => (
            <button
              aria-label={label}
              className={index === 0 ? "active" : ""}
              type="button"
              key={tone}
            >
              <Icon name="flag" />
            </button>
          ))}
        </div>
      </div>
      <SheetLine icon="calendar" label="Due date" value="May 6, 2025  10:00 AM" />
      <div className="sheet-card subtask-sheet">
        <div>
          <Icon name="filter" />
          <span>Subtasks</span>
          <em>2</em>
        </div>
        <label>
          <span className="subtask-check" /> Gather data from analytics
        </label>
        <label>
          <span className="subtask-check" /> Write executive summary
        </label>
        <button type="button">
          <Icon name="plus" />
          Add subtask
        </button>
      </div>
      <SheetLine icon="note" label="Notes" value="Include key metrics and insights." />
      <button className="save-sheet" type="button" onClick={onSave}>
        Save
      </button>
    </div>
  );
}

function SheetLine({ icon, label, value }) {
  return (
    <div className="sheet-card sheet-line">
      <Icon name={icon} />
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function FlowBoard() {
  const steps = [
    ["Open quick add", "The desktop inline add field and mobile FAB both start the same task object."],
    ["Add task details", "Priority, due date, project, subtasks, and notes keep the object structured."],
    ["Review in Today", "New work appears in Focus with the same row anatomy as existing tasks."],
    ["Complete task", "Checkbox transition moves the item into Done while preserving undo."],
    ["Confirm momentum", "Progress updates and completed tasks stay visible without competing with active work."]
  ];

  return (
    <section className="screen-block" id="flow">
      <FrameLabel
        kicker="Bonus prototype flow"
        title="Create -> Complete Task Flow"
        description="The bonus material shows the interaction model Frost asked for: screens, assets, flow, and notes."
      />
      <div className="flow-board">
        {steps.map(([title, body], index) => (
          <article key={title}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <h3>{title}</h3>
            <p>{body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function SystemBoard({ tasks, toggleTask }) {
  const sampleActive = tasks.find((task) => !task.completed);
  const sampleDone = tasks.find((task) => task.completed);

  return (
    <section className="screen-block" id="system">
      <FrameLabel
        kicker="Design system and Figma organization"
        title="Tokens, Components, and File Structure"
        description="Built for consistency: reusable rows, chips, buttons, mobile cards, sheets, and clear naming."
      />
      <div className="system-grid">
        <article className="system-card tokens-card">
          <h3>Color Tokens</h3>
          <div className="token-grid">
            {tokens.map(([name, value]) => (
              <div key={name}>
                <span style={{ background: value }} />
                <strong>{name}</strong>
                <small>{value}</small>
              </div>
            ))}
          </div>
        </article>
        <article className="system-card type-card">
          <h3>Typography</h3>
          <div>
            <p className="type-display">Today Dashboard</p>
            <p className="type-title">Section title / 18 Semibold</p>
            <p className="type-body">Body copy / 15 Regular with comfortable line height.</p>
            <p className="type-caption">Caption / 12 Medium for metadata and counters.</p>
          </div>
        </article>
        <article className="system-card component-card">
          <h3>Task Row Variants</h3>
          <div className="rows">
            <TaskRow
              task={sampleActive}
              selected
              onSelect={() => {}}
              onToggle={() => toggleTask(sampleActive.id)}
            />
            <TaskRow
              task={{ ...sampleActive, id: "medium", title: "Review invoice notes", priority: "Medium", priorityTone: "yellow" }}
              selected={false}
              onSelect={() => {}}
              onToggle={() => {}}
            />
            <TaskRow
              task={sampleDone}
              selected={false}
              onSelect={() => {}}
              onToggle={() => toggleTask(sampleDone.id)}
            />
          </div>
        </article>
        <article className="system-card organization-card">
          <h3>Figma Page Structure</h3>
          <ul>
            <li>00 Cover</li>
            <li>01 Brief + UX Notes</li>
            <li>02 Desktop / Today Dashboard</li>
            <li>03 Mobile / Today List</li>
            <li>04 Components</li>
            <li>05 Prototype Flow</li>
            <li>06 Design Tokens</li>
          </ul>
        </article>
        <article className="system-card states-card">
          <h3>Interaction States</h3>
          <div className="state-list">
            <span>Default</span>
            <span>Hover</span>
            <span>Selected</span>
            <span>Editing</span>
            <span>Completed</span>
            <span>Undo toast</span>
            <span>Empty Today</span>
            <span>No search results</span>
          </div>
        </article>
        <article className="system-card handoff-card">
          <h3>Layer Naming Examples</h3>
          <code>Desktop / Today Dashboard</code>
          <code>Task Row / Checkbox / Default</code>
          <code>Task Row / Metadata / Due Time</code>
          <code>Mobile / Bottom Sheet / Edit Task</code>
          <code>Component / Chip / Priority High</code>
        </article>
      </div>
    </section>
  );
}

function FrameLabel({ kicker, title, description }) {
  return (
    <div className="frame-label">
      <span>{kicker}</span>
      <div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </div>
  );
}

function App() {
  const [tasks, setTasks] = useState(initialTasks);
  const [selectedId, setSelectedId] = useState("weekly-report");

  const stats = useMemo(() => {
    const completed = tasks.filter((task) => task.completed).length;
    return { completed, active: tasks.length - completed, total: tasks.length };
  }, [tasks]);

  function toggleTask(id) {
    setTasks((current) =>
      current.map((task) =>
        task.id === id
          ? {
              ...task,
              completed: !task.completed,
              group: task.completed ? "Focus" : "Done",
              status: task.completed ? "In Progress" : "Done"
            }
          : task
      )
    );
  }

  function createTask(title) {
    const id = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${Date.now()}`;
    const nextTask = {
      id,
      title,
      project: "Work",
      projectTone: "blue",
      priority: "High",
      priorityTone: "amber",
      due: "Today, 4:30 PM",
      group: "Focus",
      completed: false,
      notes: "New task created from the quick add flow.",
      subtasks: [{ label: "Add details", done: false }],
      status: "Not Started",
      estimate: "30m",
      assignee: userProfile.name
    };
    setTasks((current) => [nextTask, ...current]);
    return id;
  }

  return (
    <div className="app-shell">
      <header className="submission-header">
        <div>
          <BrandWordmark />
          <p>UI Designer Technical Exam Prototype</p>
        </div>
        <nav aria-label="Prototype sections">
          <a href="#desktop">Desktop</a>
          <a href="#mobile">Mobile</a>
          <a href="#flow">Flow</a>
          <a href="#system">System</a>
        </nav>
        <div className="submission-stats">
          <span>{stats.total} tasks</span>
          <span>{stats.completed} completed</span>
          <span>{stats.active} pending</span>
        </div>
      </header>

      <main>
        <section className="cover-panel" aria-labelledby="cover-title">
          <div>
            <span className="cover-mark">Technical Exam Submission</span>
            <h1 id="cover-title">A calm productivity cockpit for getting today clear.</h1>
            <p>
              BusyBee balances fast capture, visible progress, and clear completed work.
              The file is structured to convert into Figma pages, components, variants, and
              prototype links.
            </p>
          </div>
          <div className="cover-checklist">
            <strong>Included</strong>
            <span>Desktop screen</span>
            <span>Mobile screen</span>
            <span>Task create and complete flow</span>
            <span>Design tokens and component variants</span>
          </div>
        </section>

        <DesktopScreen
          tasks={tasks}
          selectedId={selectedId}
          setSelectedId={setSelectedId}
          toggleTask={toggleTask}
          createTask={createTask}
        />
        <PhoneFrame tasks={tasks} toggleTask={toggleTask} createTask={createTask} />
        <FlowBoard />
        <SystemBoard tasks={tasks} toggleTask={toggleTask} />
      </main>
    </div>
  );
}

export default App;
