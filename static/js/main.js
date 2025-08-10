async function postJSON(url, data){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  });
  if(!res.ok){ throw new Error('Ошибка отправки'); }
  return await res.json();
}

function formToJSON(form){
  const data = Object.fromEntries(new FormData(form).entries());
  Object.keys(data).forEach(k => { if(data[k]==='') data[k]=undefined; });
  return data;
}

document.addEventListener('DOMContentLoaded', () => {
  const leadForm = document.getElementById('leadForm');
  if(leadForm){
    leadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = formToJSON(leadForm);
      try{
        await postJSON('/api/lead', data);
        window.location = '/thanks';
      }catch(err){
        alert('Не удалось отправить заявку. Попробуйте ещё раз.');
      }
    });
  }

  const feedbackForm = document.getElementById('feedbackForm');
  if(feedbackForm){
    feedbackForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = formToJSON(feedbackForm);
      try{
        await postJSON('/api/feedback', data);
        alert('Спасибо! Мы получили ваш вопрос.');
        feedbackForm.reset();
      }catch(err){
        alert('Не удалось отправить сообщение.');
      }
    });
  }
});
