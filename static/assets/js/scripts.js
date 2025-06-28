$(document).ready(function()
{
  $(".menu-toggle").click(function(){
      $("header").toggleClass("display");
  });

  $('.post-wrapper').slick({
  slidesToShow: 4,
  slidesToScroll: 1,
  autoplay: true,
  autoplaySpeed: 2000,
  nextArrow:$(".next"),
  prevArrow:$(".prev"),
  responsive: [
    {
      breakpoint: 1024,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 3,
        infinite: true,
        dots: true
      }
    },
    {
      breakpoint: 950,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 2
      }
    },
    {
      breakpoint: 650,
      settings: {
        slidesToShow: 1,
        slidesToScroll: 1
      }
    }
  ]
});

   $('.media-slider').slick({
  slidesToShow: 1,
  slidesToScroll: 1,
  autoplay: true,
  autoplaySpeed:2000,
  arrows:false,
  dots:false
      });

  /* Org-Donate */
   //Default state
      var defaultDonate = $("input:radio[name=select-amount]:checked");


      if (defaultDonate.length>0) {
          donateAmount(defaultDonate);
      };

      function donateAmount(selectedDonateAmount){
         var donate_amount = selectedDonateAmount.attr("select-amount");
         $('#selectedAmount').val(donate_amount);

         $("input:radio[name=select-amount]:not(:checked)").next().removeClass('active');
         selectedDonateAmount.next().addClass('active'); 
      }

     $("input:radio[name=select-amount]").bind('change','checked', function() {
          var selectedDonateAmount = $(this);
          donateAmount(selectedDonateAmount);
      });

  //Custom Amount
     $(".custom-input-display").click(function(){
        $("#custom-input").show();
     });

     $("#customAmount").on('input', function() {
          var input = $(this);
          $('#selectedAmount').val(input.val());
      });

  });

ClassicEditor
    .create( document.querySelector( '#body' ), {
        toolbar: [ 'heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote' ],
        heading: {
            options: [
                { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' }
            ]
        }
    } )
    .catch( error => {
        console.log( error );
    } );



