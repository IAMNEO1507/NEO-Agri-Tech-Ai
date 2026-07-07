// Generic form validation for crop yield inputs
(function(){
    function showError(el, msg) {
        el.classList.add('input-error');
        let next = el.nextElementSibling;
        if (!next || !next.classList.contains('error-text')) {
            next = document.createElement('div');
            next.className = 'error-text';
            el.parentNode.insertBefore(next, el.nextSibling);
        }
        next.textContent = msg;
    }

    function clearError(el) {
        el.classList.remove('input-error');
        let next = el.nextElementSibling;
        if (next && next.classList.contains('error-text')) next.textContent = '';
    }

    function isNumeric(v){
        return v !== '' && !isNaN(v);
    }

    function validateYieldForm(form){
        let valid = true;
        const fields = [
            {name:'N', label:'Nitrogen (N)', min:0},
            {name:'P', label:'Phosphorus (P)', min:0},
            {name:'K', label:'Potassium (K)', min:0},
            {name:'temperature', label:'Temperature', min:0},
            {name:'humidity', label:'Humidity', min:0, max:100},
            {name:'ph', label:'pH', min:0, max:14},
            {name:'rainfall', label:'Rainfall', min:0}
        ];

        fields.forEach(f => {
            const el = form.querySelector('[name="'+f.name+'"]');
            if (!el) return;
            clearError(el);
            const val = el.value.trim();
            if (val === ''){
                showError(el, f.label + ' is required');
                valid = false;
                return;
            }
            if (!isNumeric(val)){
                showError(el, f.label + ' must be a number');
                valid = false;
                return;
            }
            const num = parseFloat(val);
            if (typeof f.min === 'number' && num < f.min){
                showError(el, f.label + ' must be ≥ ' + f.min);
                valid = false;
                return;
            }
            if (typeof f.max === 'number' && num > f.max){
                showError(el, f.label + ' must be ≤ ' + f.max);
                valid = false;
                return;
            }
        });

        return valid;
    }

    document.addEventListener('DOMContentLoaded', function(){
        const form = document.getElementById('yieldForm');
        if (!form) return;

        // inject minimal styles
        const style = document.createElement('style');
        style.textContent = '\n.input-error{border:2px solid #ef4444!important;}\n.error-text{color:#ef4444;font-size:0.9rem;margin-top:4px;}\n';
        document.head.appendChild(style);

        form.addEventListener('submit', function(e){
            // prevent default submission until we validate
            e.preventDefault();
            // clear all previous errors
            Array.from(form.querySelectorAll('.input-error')).forEach(el=>el.classList.remove('input-error'));
            Array.from(form.querySelectorAll('.error-text')).forEach(el=>el.textContent='');

            const ok = validateYieldForm(form);
            if (ok){
                form.submit();
            } else {
                const firstError = form.querySelector('.input-error');
                if (firstError && typeof firstError.scrollIntoView === 'function'){
                    firstError.scrollIntoView({behavior:'smooth', block:'center'});
                }
            }
        });
    });
})();
