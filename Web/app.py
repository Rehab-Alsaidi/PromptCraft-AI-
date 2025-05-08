from flask import Flask, request, jsonify, render_template, session
from langchain_google_genai import ChatGoogleGenerativeAI
from langdetect import detect
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize the Google Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    google_api_key="AIzaSyBGGwMOLZg1jyb3cTm-18AFqRzhF3wtpiw",
    temperature=0.7
)

# Enhanced translations with framework descriptions
translations = {
    'en': {
        'title': 'PromptCraft AI',
        'description': 'Transform your ideas into perfectly structured prompts with advanced AI frameworks',
        'prompt_label': 'YOUR PROMPT',
        'framework_label': 'SELECT FRAMEWORK',
        'broke_option': 'BROKE Framework',
        'crispe_option': 'CRISPE Framework',
        'structured_option': 'Structured Template',
        'enhance_button': 'Enhance Prompt',
        'loading_text': 'Crafting your perfect prompt...',
        'original_prompt': 'Original Prompt:',
        'enhanced_prompt': 'Enhanced Prompt:',
        'copy_button': 'Copy',
        'language_switch': 'العربية',
        'current_language': 'English',
        'alert_empty_prompt': 'Please enter a prompt',
        'no_enhancement': 'No enhancement returned.',
        'server_error': 'Server error',
        'unknown_error': 'Unknown error',
        'network_error': 'Network error',
        'copied_text': 'Copied!',
        'copy_failed': 'Failed to copy',
        'language_switch_failed': 'Language switch failed',
        
        # Framework tabs
        'broke_tab': 'BROKE',
        'crispe_tab': 'CRISPE',
        'structured_tab': 'STRUCTURED',
        
        # Framework titles
        'broke_title': 'BROKE Framework',
        'crispe_title': 'CRISPE Framework',
        'structured_title': 'Structured Prompt Template',
        
        # BROKE framework items
        'broke_background': 'Background',
        'broke_background_desc': 'Provides relevant context and background information to set the stage for the prompt.',
        'broke_role': 'Role',
        'broke_role_desc': 'Defines the role and responsibilities the AI should assume when responding.',
        'broke_objectives': 'Objectives',
        'broke_objectives_desc': 'Lists clear and specific objectives the prompt should accomplish.',
        'broke_key_results': 'Key Results',
        'broke_key_results_desc': 'Specifies measurable outcomes and success criteria for the response.',
        'broke_evolve': 'Evolve',
        'broke_evolve_desc': 'Suggests how the task can grow or adapt for future iterations.',
        
        # CRISPE framework items
        'crispe_context': 'Context',
        'crispe_context_desc': 'Provides background information the AI needs to understand the task.',
        'crispe_role': 'Role',
        'crispe_role_desc': 'Assigns a specific role or persona for the AI to adopt.',
        'crispe_input': 'Input',
        'crispe_input_desc': 'States the user\'s input or data that needs processing.',
        'crispe_steps': 'Steps',
        'crispe_steps_desc': 'Describes the steps the AI should follow to complete the task.',
        'crispe_parameters': 'Parameters',
        'crispe_parameters_desc': 'Sets constraints or preferences for the response.',
        'crispe_end_goal': 'End Goal',
        'crispe_end_goal_desc': 'States the final objective expected from the AI.',
        
        # Structured framework items
        'structured_role': 'Role',
        'structured_role_desc': 'Defines the role or persona the AI should embody.',
        'structured_background': 'Background',
        'structured_background_desc': 'Provides relevant context for the prompt.',
        'structured_constraints': 'Constraints',
        'structured_constraints_desc': 'Lists any limitations or boundaries for the response.',
        'structured_goals': 'Goals',
        'structured_goals_desc': 'States the objectives the prompt should achieve.',
        'structured_examples': 'Examples',
        'structured_examples_desc': 'Provides relevant examples to guide the response.',
        'structured_workflows': 'Workflows',
        'structured_workflows_desc': 'Describes the step-by-step process the AI should follow.'
    },
    'ar': {
        'title': 'بromptCraft الذكاء الاصطناعي',
        'description': 'حول أفكارك إلى أوامر مهيكلة بشكل مثالي باستخدام أطر الذكاء الاصطناعي المتقدمة',
        'prompt_label': 'أمرك',
        'framework_label': 'اختر إطار العمل',
        'broke_option': 'إطار BROKE',
        'crispe_option': 'إطار CRISPE',
        'structured_option': 'قالب منظم',
        'enhance_button': 'تحسين الأمر',
        'loading_text': 'جاري إنشاء الأمر المثالي...',
        'original_prompt': 'الأمر الأصلي:',
        'enhanced_prompt': 'الأمر المحسن:',
        'copy_button': 'نسخ',
        'language_switch': 'English',
        'current_language': 'العربية',
        'alert_empty_prompt': 'الرجاء إدخال أمر',
        'no_enhancement': 'لم يتم إرجاع أي تحسين.',
        'server_error': 'خطأ في الخادم',
        'unknown_error': 'خطأ غير معروف',
        'network_error': 'خطأ في الشبكة',
        'copied_text': 'تم النسخ!',
        'copy_failed': 'فشل النسخ',
        'language_switch_failed': 'فشل تغيير اللغة',
        
        # Framework tabs
        'broke_tab': 'BROKE',
        'crispe_tab': 'CRISPE',
        'structured_tab': 'منظم',
        
        # Framework titles
        'broke_title': 'إطار BROKE',
        'crispe_title': 'إطار CRISPE',
        'structured_title': 'قالب الأمر المنظم',
        
        # BROKE framework items
        'broke_background': 'الخلفية',
        'broke_background_desc': 'يوفر السياق والخلفية ذات الصلة لإعداد المسرح للأمر.',
        'broke_role': 'الدور',
        'broke_role_desc': 'يحدد الدور والمسؤوليات التي يجب أن يتبناها الذكاء الاصطناعي عند الرد.',
        'broke_objectives': 'الأهداف',
        'broke_objectives_desc': 'يسرد أهدافًا واضحة ومحددة يجب أن يحققها الأمر.',
        'broke_key_results': 'النتائج الرئيسية',
        'broke_key_results_desc': 'يحدد النتائج القابلة للقياس ومعايير النجاح للرد.',
        'broke_evolve': 'تطور',
        'broke_evolve_desc': 'يقترح كيف يمكن للمهمة أن تنمو أو تتكيف للتكرارات المستقبلية.',
        
        # CRISPE framework items
        'crispe_context': 'السياق',
        'crispe_context_desc': 'يوفر معلومات أساسية يحتاجها الذكاء الاصطناعي لفهم المهمة.',
        'crispe_role': 'الدور',
        'crispe_role_desc': 'يعين دورًا أو شخصية محددة للذكاء الاصطناعي لتبنيها.',
        'crispe_input': 'الإدخال',
        'crispe_input_desc': 'يحدد إدخال المستخدم أو البيانات التي تحتاج إلى معالجة.',
        'crispe_steps': 'الخطوات',
        'crispe_steps_desc': 'يصف الخطوات التي يجب أن يتبعها الذكاء الاصطناعي لإكمال المهمة.',
        'crispe_parameters': 'المعايير',
        'crispe_parameters_desc': 'يحدد القيود أو التفضيلات للرد.',
        'crispe_end_goal': 'الهدف النهائي',
        'crispe_end_goal_desc': 'يحدد الهدف النهائي المتوقع من الذكاء الاصطناعي.',
        
        # Structured framework items
        'structured_role': 'الدور',
        'structured_role_desc': 'يحدد الدور أو الشخصية التي يجب أن يجسدها الذكاء الاصطناعي.',
        'structured_background': 'الخلفية',
        'structured_background_desc': 'يوفر السياق ذو الصلة للأمر.',
        'structured_constraints': 'القيود',
        'structured_constraints_desc': 'يسرد أي قيود أو حدود للرد.',
        'structured_goals': 'الأهداف',
        'structured_goals_desc': 'يحدد الأهداف التي يجب أن يحققها الأمر.',
        'structured_examples': 'أمثلة',
        'structured_examples_desc': 'يوفر أمثلة ذات صلة لتوجيه الرد.',
        'structured_workflows': 'سير العمل',
        'structured_workflows_desc': 'يصف عملية خطوة بخطوة يجب أن يتبعها الذكاء الاصطناعي.'
    }
}

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'

def enhance_prompt(user_prompt, framework):
    lang = detect_language(user_prompt)
    target_lang = 'arabic' if lang == 'ar' else 'english'
    
    if framework == "BROKE":
        system_prompt = f"""You are an expert prompt engineer. Enhance the following user prompt using the BROKE framework in {target_lang}.
        Structure your response exactly as follows in {target_lang}:

        ```
        B - Background: Provide relevant context and background information
        R - Role: Define the role and responsibilities
        O - Objectives: List clear and specific objectives
        K - Key Results: Specify measurable outcomes and success criteria
        E - Evolve: Suggest how the task can grow or adapt

        User Prompt: {user_prompt}
        """
    elif framework == "CRISPE":
        system_prompt = f"""You are an expert prompt engineer. Enhance the following user prompt using the CRISPE framework in {target_lang}.
        Structure your response exactly as follows in {target_lang}:

        ```
        C - Context: Provide background information the model needs
        R - Role: Assign a specific role or persona to the model
        I - Input: State the user's input or data to be processed
        S - Steps: Describe the steps the model should follow
        P - Parameters: Set constraints or preferences
        E - End Goal: State the final objective or outcome

        User Prompt: {user_prompt}
        """
    elif framework == "STRUCTURED":
        system_prompt = f"""You are an expert prompt engineer. Enhance the following user prompt using the Structured Prompt Template in {target_lang}.
        Structure your response exactly as follows in {target_lang}:

        ```
        Role: [Define the role or persona]
        Background: [Provide relevant context]
        Constraints: [List any limitations or boundaries]
        Goals: [State the objectives]
        Examples: [Provide relevant examples if applicable]
        Workflows: [Describe the step-by-step process]

        User Prompt: {user_prompt}
        """
    else:
        return "Invalid framework selected"

    response = llm.invoke(system_prompt)
    return response.content

@app.route('/')
def home():
    lang = session.get('language', 'en')
    return render_template('index.html', lang=lang, translations=translations[lang])

@app.route('/switch-language', methods=['POST'])
def switch_language():
    current_lang = session.get('language', 'en')
    new_lang = 'ar' if current_lang == 'en' else 'en'
    session['language'] = new_lang
    return jsonify({'success': True, 'new_language': new_lang})

@app.route('/enhance-prompt', methods=['POST'])
def enhance_prompt_endpoint():
    try:
        data = request.get_json()
        if not data or 'prompt' not in data or 'framework' not in data:
            return jsonify({'error': 'Prompt or framework not provided'}), 400

        user_prompt = data['prompt']
        framework = data['framework']
        enhanced_prompt = enhance_prompt(user_prompt, framework)
        
        return jsonify({
            'original_prompt': user_prompt,
            'enhanced_prompt': enhanced_prompt,
            'framework': framework
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)