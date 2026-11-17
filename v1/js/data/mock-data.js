const DAY = 86400000;

export const exam = {
  id: 'exam-1',
  title: 'Quantitative Reasoning Midterm',
  lengthMinutes: 60,
  rules: [
    'Work alone. Do not use other people, websites or tools.',
    'Stay on the exam page in fullscreen until you finish.',
    'Use Request help if you have a problem. The timer pauses while help is open.',
  ],
  detected: [
    'leaving the exam page',
    'exiting fullscreen',
    'pasting into an answer field',
    'submitting an answer within 30 seconds of returning',
  ],
  questions: [
    {
      id: 'q1',
      template: 'A train travels {d} km in {t} hours. What is its average speed in km/h?',
      params: { d: [120, 150, 180, 210, 240], t: [2, 3] },
      answer: ({ d, t }) => d / t,
    },
    {
      id: 'q2',
      template: 'A box holds {a} rows of {b} items. How many items are in the box?',
      params: { a: [6, 7, 8, 9], b: [4, 5, 6, 7] },
      answer: ({ a, b }) => a * b,
    },
    {
      id: 'q3',
      template: 'A shirt costs {p} dollars and is discounted by {r} percent. What is the sale price in dollars?',
      params: { p: [40, 60, 80, 100], r: [10, 20, 25, 50] },
      answer: ({ p, r }) => (p * (100 - r)) / 100,
    },
  ],
};

// s3 and s4 both answer 50 on q2, which is wrong for every q2 version (no a*b equals 50).
// A live student who also answers 50 completes a group of 3.
export const SHARED_INCORRECT_Q2 = 50;

export const students = [
  { id: 's1', name: 'Student A', extraTimePct: 50, playable: true },
  { id: 's2', name: 'Student B', extraTimePct: 0, playable: true },
  {
    id: 's3', name: 'Student C', extraTimePct: 0, playable: false,
    prefilledAnswers: {
      q1: { version: { d: 180, t: 3 }, value: 60 },
      q2: { version: { a: 6, b: 7 }, value: SHARED_INCORRECT_Q2 },
      q3: { version: { p: 80, r: 25 }, value: 60 },
    },
  },
  {
    id: 's4', name: 'Student D', extraTimePct: 0, playable: false,
    prefilledAnswers: {
      q1: { version: { d: 240, t: 2 }, value: 120 },
      q2: { version: { a: 9, b: 4 }, value: SHARED_INCORRECT_Q2 },
      q3: { version: { p: 60, r: 10 }, value: 54 },
    },
  },
  {
    id: 's5', name: 'Student E', extraTimePct: 0, playable: false,
    prefilledAnswers: {
      q1: { version: { d: 150, t: 3 }, value: 50 },
      q2: { version: { a: 8, b: 5 }, value: 40 },
      q3: { version: { p: 100, r: 50 }, value: 50 },
    },
  },
];

const requestedAt = Date.UTC(2026, 10, 12, 10, 0);

export const seed = {
  role: 'student',
  currentStudentId: 's1',
  students,
  sessions: {},
  signals: [
    {
      id: 'sig-s1', studentId: 's3', type: 'paste',
      at: Date.UTC(2026, 10, 11, 14, 12), until: null, details: { questionId: 'q3' },
    },
    {
      id: 'sig-s2', studentId: 's4', type: 'page_leave',
      at: Date.UTC(2026, 10, 11, 14, 20), until: Date.UTC(2026, 10, 11, 14, 22), details: {},
    },
  ],
  flags: [
    {
      id: 'flag-s1', signalId: 'sig-s1', studentId: 's3', state: 'explanation_requested',
      createdAt: Date.UTC(2026, 10, 11, 15, 0),
      explanationRequestedAt: requestedAt, deadline: requestedAt + 3 * DAY,
      explanation: null, referralId: null,
    },
    {
      id: 'flag-s2', signalId: 'sig-s2', studentId: 's4', state: 'explained',
      createdAt: Date.UTC(2026, 10, 11, 15, 0),
      explanationRequestedAt: requestedAt, deadline: requestedAt + 3 * DAY,
      explanation: {
        text: 'My laptop battery warning covered the screen and I clicked away to plug it in.',
        submittedAt: requestedAt + DAY,
      },
      referralId: null,
    },
  ],
  groups: [],
  referrals: [],
};
