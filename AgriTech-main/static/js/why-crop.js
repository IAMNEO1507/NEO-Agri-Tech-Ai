// Simple filter for 'Why This Crop' cards
document.addEventListener('DOMContentLoaded', function(){
    const select = document.getElementById('whyCropFilter');
    const container = document.getElementById('whyCropCards');
    if (!select || !container) return;

    function applyFilter(){
        const val = select.value;
        const cards = container.querySelectorAll('.feature-card');
        cards.forEach(c=>{
            if (val === 'all' || c.dataset.crop === val){
                c.style.display = '';
            } else {
                c.style.display = 'none';
            }
        });
    }

    select.addEventListener('change', applyFilter);

    // If query param ?crop=maize present, pre-filter
    const params = new URLSearchParams(window.location.search);
    const crop = params.get('crop');
    if (crop){
        const opt = Array.from(select.options).find(o=>o.value===crop.toLowerCase());
        if (opt){ select.value = opt.value; }
    }
    applyFilter();
});
