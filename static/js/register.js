const form = document.getElementById('regForm');
const stateSelect = document.getElementById('state');
const districtSelect = document.getElementById('district');
const submitBtn = document.getElementById('submitBtn');
const msg = document.getElementById('msg');

let statesData = {};

const value = (id) => document.getElementById(id).value.trim();

function fillOptions(select, items, placeholder) {
  select.innerHTML = '';
  const first = document.createElement('option');
  first.value = '';
  first.textContent = placeholder;
  select.appendChild(first);

  items.forEach((item) => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item;
    select.appendChild(opt);
  });
}

function showMessage(text, isSuccess) {
  msg.className = isSuccess ? 'msg success' : 'msg error';
  msg.textContent = text;
}

fetch(form.dataset.districtsUrl)
  .then((res) => res.json())
  .then((data) => {
    statesData = data;
    fillOptions(stateSelect, Object.keys(data).sort(), '-- Select State --');
  })
  .catch(() => showMessage('Could not load states list. Please refresh.', false));

stateSelect.addEventListener('change', () => {
  const districts = statesData[stateSelect.value];
  if (!districts) {
    fillOptions(districtSelect, [], '-- Select State first --');
    districtSelect.disabled = true;
    return;
  }
  fillOptions(districtSelect, districts, '-- Select District --');
  districtSelect.disabled = false;
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  submitBtn.disabled = true;
  msg.textContent = '';

  const payload = {
    name: value('name'),
    village: value('village'),
    state: value('state'),
    district: value('district'),
    mobile: value('mobile'),
    age: parseInt(value('age'), 10),
    work: value('work'),
  };

  try {
    const res = await fetch('/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    if (res.ok) {
      showMessage('Registered successfully!', true);
      form.reset();
      stateSelect.dispatchEvent(new Event('change'));
    } else {
      showMessage(data.detail, false);
    }
  } catch (err) {
    showMessage('Network error. Please try again.', false);
  } finally {
    submitBtn.disabled = false;
  }
});