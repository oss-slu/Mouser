import random
from CTkMessagebox import CTkMessagebox
from customtkinter import *

from api_services.services import *


def open_annotation_dialog(self, experiment_id=None):
        annotation_dialog = CTkToplevel(self)
        annotation_dialog.title("Add Annotation")
        annotation_dialog.geometry("400x220")

        label = CTkLabel(annotation_dialog, text="Enter your annotation:")
        label.pack(pady=10)

        annotation_entry = CTkTextbox(annotation_dialog, height=80, width=350)
        annotation_entry.pack(pady=10)

        char_count_label = CTkLabel(annotation_dialog, text="Characters: 0/100")
        char_count_label.pack(pady=(0, 10))

        def update_char_count(event=None):
            current_text = annotation_entry.get("1.0", "end")[:-1]
            char_count = len(current_text)
            if char_count > 100:
                annotation_entry.delete("1.0+100c", "end")
                char_count = 100
            char_count_label.configure(text=f"Characters: {char_count}/100")

        annotation_entry.bind("<KeyRelease>", update_char_count)

        def submit_annotation_ui():
            annotation_text = annotation_entry.get("1.0", "end").strip()
            if annotation_text:
                eid = experiment_id if experiment_id else str(random.randint(1000, 9999))
                success, error = submit_annotation(annotation_text, eid)
                if success:
                    CTkMessagebox(
                        message=f"Annotation submitted and stored!\nExperiment ID: {eid}",
                        title="Success",
                        icon="check"
                    )
                    print(f"Experiment ID used: {eid}")
                    annotation_dialog.destroy()
                else:
                    CTkMessagebox(
                        message=f"Failed to store annotation: {error}",
                        title="Error",
                        icon="cancel"
                    )
            else:
                CTkMessagebox(
                    message="Annotation cannot be empty.",
                    title="Error",
                    icon="cancel"
                )

        submit_btn = CTkButton(annotation_dialog, text="Submit", command=submit_annotation_ui)
        submit_btn.pack(pady=10)


def open_edit_annotations_dialog(self, experiment_id=None):
        edit_dialog = CTkToplevel(self)
        edit_dialog.title("Edit Annotations")
        edit_dialog.geometry("400x350")

        label = CTkLabel(edit_dialog, text="Enter 4-digit Experiment ID:")
        label.pack(pady=10)

        id_entry = CTkEntry(edit_dialog, width=80)
        id_entry.pack(pady=5)

        listbox = CTkTextbox(edit_dialog, height=120, width=350)
        listbox.pack(pady=10)
        listbox.configure(state="disabled")

        selected_index = [None]

        def load_annotations_for_editing():
            eid = experiment_id if experiment_id else id_entry.get().strip()
            annotations, error = get_annotations(eid)
            listbox.configure(state="normal")
            listbox.delete("1.0", "end")
            if annotations:
                for idx, ann in enumerate(annotations):
                    text = ann.get("body", {}).get("value", "[No Value]")
                    listbox.insert("end", f"{idx + 1}. {text}\n")
                selected_index[0] = annotations
            else:
                listbox.insert("end", f"Error: {error or 'No annotations found.'}")
            listbox.configure(state="disabled")

        def edit_selected_annotation():
            annotation_list = selected_index[0]
            if not annotation_list:
                return
            old = annotation_list[0]
            edit_box = CTkToplevel(self)
            edit_box.title("Edit Annotation")
            edit_box.geometry("400x200")

            textbox = CTkTextbox(edit_box, height=80, width=350)
            textbox.insert("1.0", old["body"]["value"])
            textbox.pack(pady=10)

            def update_annotation():
                new_text = textbox.get("1.0", "end").strip()
                if new_text and new_text != old["body"]["value"]:
                    updated = old.copy()
                    updated["body"]["value"] = new_text
                    annotation_id = old.get("@id") or old.get("id", "")
                    success, error = update_annotation(annotation_id, new_text)
                    if success:
                        CTkMessagebox(title="Success", message="Annotation updated!", icon="check")
                        edit_box.destroy()
                    else:
                        CTkMessagebox(title="Error", message=f"Failed to update: {error}", icon="cancel")

            submit_btn = CTkButton(edit_box, text="Submit", command=update_annotation)
            submit_btn.pack(pady=10)

        fetch_btn = CTkButton(edit_dialog, text="Fetch", command=load_annotations_for_editing)
        fetch_btn.pack(pady=5)

        edit_btn = CTkButton(edit_dialog, text="Edit", command=edit_selected_annotation)
        edit_btn.pack(pady=5)


def open_load_annotations_dialog(self, experiment_id=None):
        load_dialog = CTkToplevel(self)
        load_dialog.title("Load Annotations")
        load_dialog.geometry("400x340")

        label = CTkLabel(load_dialog, text="Enter 4-digit Experiment ID:")
        label.pack(pady=10)

        e_id = CTkEntry(load_dialog, width=80)
        e_id.pack(pady=5)

        annotations_box = CTkTextbox(load_dialog, height=120, width=350, state="disabled")
        annotations_box.pack(pady=10)

        annotations = []

        def fetch_and_display():
            nonlocal annotations
            eid = experiment_id if experiment_id else e_id.get().strip()
            if len(eid) != 4 or not eid.isdigit():
                CTkMessagebox(
                    message="Please enter a valid 4-digit Experiment ID.",
                    title="Error",
                    icon="cancel"
                )
                delete_btn.configure(state="disabled")
                edit_btn.configure(state="disabled")
                return

            annotations, error = get_annotations(eid)
            annotations_box.configure(state="normal")
            annotations_box.delete("1.0", "end")
            delete_btn.configure(state="disabled")
            edit_btn.configure(state="disabled")

            if annotations:
                for i in annotations:
                    value = i.get("body", {}).get("value", "[No Value]")
                    annotations_box.insert("end", f"{value}\n")
                delete_btn.configure(state="normal")
                edit_btn.configure(state="normal")
            else:
                annotations_box.insert("end", f"No annotations found.\nError: {error if error else ''}")
                delete_btn.configure(state="disabled")
                edit_btn.configure(state="disabled")
            annotations_box.configure(state="disabled")

        def delete_annotations_ui():
            eid = experiment_id if experiment_id else e_id.get().strip()
            if len(eid) != 4 or not eid.isdigit():
                CTkMessagebox(
                    message="Please enter a valid 4-digit Experiment ID.",
                    title="Error",
                    icon="cancel"
                )
                return

            success, error = delete_annotations_by_experiment(eid)
            if success:
                CTkMessagebox(
                    message="All annotations for this experiment deleted successfully!",
                    title="Success",
                    icon="check"
                )
                fetch_and_display()
            else:
                CTkMessagebox(
                    message=f"Failed to delete annotations: {error}",
                    title="Error",
                    icon="cancel"
                )

        button_frame = CTkFrame(load_dialog)
        button_frame.pack(pady=5)

        fetch_btn = CTkButton(button_frame, text="Fetch", command=fetch_and_display)
        fetch_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        delete_btn = CTkButton(button_frame, text="Delete", command=delete_annotations_ui, state="disabled")
        delete_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        edit_btn = CTkButton(button_frame, text="Edit", state="disabled")
        edit_btn.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        button_frame.grid_columnconfigure(2, weight=1)

        def edit_selected_annotation():
            if not annotations:
                return
            old = annotations[0]
            edit_box = CTkToplevel(self)
            edit_box.title("Edit Annotation")
            edit_box.geometry("400x200")

            textbox = CTkTextbox(edit_box, height=80, width=350)
            textbox.insert("1.0", old["body"]["value"])
            textbox.pack(pady=10)

            def update_annotation_ui():
                new_text = textbox.get("1.0", "end").strip()
                if new_text and new_text != old["body"]["value"]:
                    annotation_id = old.get("@id") or old.get("id", "")
                    success, error = update_annotation(annotation_id, new_text)
                    if success:
                        CTkMessagebox(title="Success", message="Annotation updated!", icon="check")
                        edit_box.destroy()
                    else:
                        CTkMessagebox(title="Error", message=f"Failed to update: {error}", icon="cancel")

            submit_btn = CTkButton(edit_box, text="Submit", command=update_annotation_ui)
            submit_btn.pack(pady=10)

        edit_btn.configure(command=edit_selected_annotation)

        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)


class Experiment:
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id
