import json
from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from fuzzywuzzy import process
from .models import Student, Attendance
from django.shortcuts import render
import google.generativeai as genai
import re


def attendance_page(request):
    return render(request, "index.html")

class mark_attendance(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("\U0001F4E5 Received POST request")
            data = request.data
            spoken_name = data.get("name")
            print(f"\U0001F50D Extracted Name: {spoken_name}")

            if not spoken_name:
                return Response({"success": False, "message": "No name received"}, status=status.HTTP_400_BAD_REQUEST)

            student_names = list(Student.objects.values_list("name", flat=True))
            print(f"\U0001F4CB Student Names: {student_names}")

            #best_match, score = process.extractOne(spoken_name, student_names) if student_names else (None, 0)
            #print(f"\U0001F3AF Best Match: {best_match}, Score: {score}")

            matches = process.extract(spoken_name, student_names, limit=5)  # Get top 5 matches
            print(f"\U0001F3AF Matches: {matches}")

            best_matches = [match for match in matches if match[1] > 80]
            print(f"Best Matches: {best_matches}")

            # if best_match and score > 80:
            if best_matches:

                if len(best_matches) > 1 and best_matches[0][1] == best_matches[1][1]:
                    return Response({"success": False, "message": f"Multiple names exists with given name, Speak your full name"})
                
                student = Student.objects.get(name=best_matches[0][0])
                today = date.today()

                if Attendance.objects.filter(student=student, date=today).exists():
                    print(f"⚠️ Attendance already marked for {student.name}")
                    return Response({"success": False, "message": f"Attendance already marked for {student.name}"})

                Attendance.objects.create(student=student)
                print(f"✅ Attendance marked for {student.name}")
                return Response({"success": True, "name": student.name, "message": f"Attendance marked for {student.name}"})

            print("❌ Name not recognized")
            return Response({"success": False, "message": "Name not recognized. Try again."}, status=status.HTTP_400_BAD_REQUEST)
        
        except json.JSONDecodeError:
            return Response({"success": False, "message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class responding_page(APIView):
    def post(self, request, *args, **kwargs):
        try:
            print("\U0001F4E5 Received POST request")
            data = request.data  
            spoken_sentence = data.get("spoken_response")
            print(f"\U0001F50D Extracted Name: {spoken_sentence}")

            if not spoken_sentence:
                return Response({"success": False, "message": "No name received"}, status=status.HTTP_400_BAD_REQUEST)
            genai.configure(api_key="AIzaSyDGUMCXz_L0PP5g-8fhaAULTK0q9eC_Kac")

            prompt = f"""you are a response generator. so i will give you the prompt, the prompt is formed by converting audio to text, so some words are completely formed. the prompt consists of students asking information about their attendance. using prompt you should form a one sentence response using the required variables from given variables. you should include this response in sanketh's json format.

Prompt: "{spoken_sentence}".
Variables:
1. total_number_of_working_days: this variable consists of total number number of working days.
2. number_of_days_present: this variable consists of total number of he/she was present.
3. number_of_days_absent: this variable consists of total number of he/she was absent.
4. percentage_of_present_days: this variable consists of percentage of he/she was present.
5. percentage_of_absent_days: this variable consists of percentage of he/she was absent.

sanketh's json format: {{
 name:"", //get this name from the prompt and insert in this. do not alter or correct the name retrieved from prompt.
 response: "", //this is a sentence which you are going to write using variables and prompt. you should provide reponse when reponse uses atleast one available variable else the reponse should be "Sorry I can't answer that"
 name_found: "", //this consists of 0 or 1 based on the prompt. if you find the name in prompt, value=1 else value=0
 others: "" //this consists of 0 or 1 based on prompt. if users asks for anything which requires use of above variables then value=0, else value=1
}}

you required to generate only json without comments according to given requirements and dont include unnessary sentence and only i should see json response.

Sample input:

prompt: my name is karthik, what is the total number of working days and what is my present percentage?

Sample response:
{{
  name: "Karthik",
  reponse: "the total number of working days are [total_number_of_working_days] and your present percentage is [percentage_of_present_days]",
  name_found: "1",
  others: "0"
}}
if you get only name in prompt then others is 1, and in response prompt the user to include query.
The variables will be replaced by my backend, so the required variables should be placed in similar format."""
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
        
            clean_text = re.sub(r'[#\*\-]\s?', '', response.text).strip()
            clean_text = clean_text.replace("```json", "").replace("```", "").strip()

        
            print("Raw Response2:", clean_text)

            try:
                response_json = json.loads(clean_text)
                print("Parsed JSON:", response_json)  

                if response_json.get('name_found') == "0":
                    print("Please mention your name, along with your query")
                    responses = "Please mention your name, along with your query"
                    return Response({"success": True, "message": responses}, status=status.HTTP_200_OK)

                # if response_json.get('others') == "1":
                #   print("I can only answer, questions of attendance")
                #   responses = "I can only answer, questions of attendance"
                #   return Response({"success": True, "message": responses}, status=status.HTTP_200_OK)
                
                else:

                #   if response_json.get('name_found') == "0":
                #     print("Please mention your name, along with your query")
                #     responses = "Please mention your name, along with your query"
                #     return Response({"success": True, "message": responses}, status=status.HTTP_200_OK)
                  if response_json.get('others') == "1":
                    print("I can only answer, questions of attendance")
                    # responses = "I can only answer, questions of attendance"
                    responses = response_json.get('response')
                    return Response({"success": True, "message": responses}, status=status.HTTP_200_OK)
                 
                  else:
                    name = response_json.get('name')
                    print(name)

                    student_names = list(Student.objects.values_list("name", flat=True))

                    #best_match, score = process.extractOne(name, student_names) if student_names else (None, 0)
                    matches = process.extract(name, student_names, limit=5)  # Get top 5 matches
                    print(f"Matches: {matches}")

                    best_matches = [match for match in matches if match[1] > 80]
                    print(f"Best Matches2: {best_matches}")

                    # if best_match and score > 80:
                    if not best_matches:
                        print("❌ Name not recognized")
                        return Response({"success": False, "message": "Name not recognized. Try again."}, status=status.HTTP_400_BAD_REQUEST)

                    if len(best_matches) > 1 and best_matches[0][1] == best_matches[1][1]:
                        return Response({"success": False, "message": f"Multiple names exists with given name, Speak your full name"})

                    student = Student.objects.get(name=best_matches[0][0])
                    
                    total_number_of_working_days = Attendance.objects.values('date').distinct().count()
                    number_of_days_present = Attendance.objects.filter(student=student).values('date').distinct().count()
                    number_of_days_absent = total_number_of_working_days - number_of_days_present
                    percentage_of_present_days = round(100 * (number_of_days_present/total_number_of_working_days))
                    percentage_of_absent_days = round(100 - percentage_of_present_days)

                    responses = response_json.get('response')
                    responses = responses.replace("[total_number_of_working_days]", " " + str(total_number_of_working_days))
                    responses = responses.replace("[number_of_days_present]", " " + str(number_of_days_present))
                    responses = responses.replace("[number_of_days_absent]", " " + str(number_of_days_absent))
                    responses = responses.replace("[percentage_of_present_days]", " " + str(percentage_of_present_days))
                    responses = responses.replace("[percentage_of_absent_days]", " " + str(percentage_of_absent_days))

                return Response({"success": True, "data": response_json, "message": responses}, status=status.HTTP_200_OK)

            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return e
    
        except Exception as e:
            return Response({"success": False, "message": "hii " """str(e)"""}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

def add_student(request):
    if request.method == "POST":
        name = request.POST.get("name")
        roll_number = request.POST.get("roll_number")

        if not name or not roll_number:
            return JsonResponse({"success": False, "message": "All fields are required"}, status=400)

        if Student.objects.filter(name=name).exists() or Student.objects.filter(roll_number=roll_number).exists():
            return JsonResponse({"success": False, "message": "Student already exists"}, status=400)

        Student.objects.create(name=name, roll_number=roll_number)
        return JsonResponse({"success": True, "message": "Student added successfully"})

    return render(request, "add_student.html")

def temp(request):
    return render(request,"temp.html")