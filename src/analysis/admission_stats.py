class AdmissionManager:
    """
    Класс для управления процессом зачисления:
    - расчёт конкурсной ситуации
    - определение проходного балла
    - формирование списков зачисленных
    """
    
    PROGRAM_NAMES = {
        'pm': 'Прикладная математика',
        'ivt': 'Информатика и вычислительная техника',
        'itss': 'Инфокоммуникационные технологии и системы связи',
        'ib': 'Информационная безопасность'
    }
    
    def __init__(self, applicants_data, program_capacity):
        """
        Args:
            applicants_data: словарь {program_code: [list of applicant dicts]}
            program_capacity: словарь {program_code: число мест}
        """
        self.applicants_data = applicants_data
        self.capacity = program_capacity
        self._enrolled = None  # кэш результатов распределения
        
    def _run_admission(self):
        """Внутренний метод: алгоритм распределения по приоритетам."""
        if self._enrolled is not None:
            return
        
        # Собираем всех абитуриентов в единый словарь {id: {данные + priorities}}
        all_applicants = {}
        for prog, records in self.applicants_data.items():
            for rec in records:
                aid = rec['id']
                if aid not in all_applicants:
                    all_applicants[aid] = {
                        'id': aid,
                        'consent': rec.get('consent', False),
                        'total': rec.get('total', 0),
                        'math': rec.get('math', 0),
                        'russian': rec.get('russian', 0),
                        'physicsIct': rec.get('physicsIct', 0),
                        'individual': rec.get('individual', 0),
                        'priorities': {}
                    }
                all_applicants[aid]['priorities'][prog] = rec.get('priority', 4)
        
        # Фильтруем только с согласием
        candidates = {aid: data for aid, data in all_applicants.items() if data['consent']}
        
        # Ключ сортировки: сумма баллов (убывание), при равенстве — по ID (возрастание)
        def sort_key(a):
            return (-a['total'], a['id'])
        
        # Алгоритм Deferred Acceptance
        programs = list(self.capacity.keys())
        next_priority = {aid: 1 for aid in candidates}
        queue = list(candidates.keys())
        tentative = {p: [] for p in programs}
        enrolled_program = {}
        
        while queue:
            aid = queue.pop(0)
            priority = next_priority[aid]
            applicant = candidates[aid]
            
            # Ищем программу с таким приоритетом
            target = None
            for prog, prio in applicant['priorities'].items():
                if prio == priority:
                    target = prog
                    break
            
            if target is None:
                if priority < 4:
                    next_priority[aid] = priority + 1
                    queue.append(aid)
                continue
            
            next_priority[aid] = priority + 1
            tentative[target].append(applicant)
            tentative[target].sort(key=sort_key)
            
            cap = self.capacity.get(target, 0)
            if len(tentative[target]) > cap:
                rejected = tentative[target][cap:]
                tentative[target] = tentative[target][:cap]
                for r in rejected:
                    if next_priority[r['id']] <= 4:
                        queue.append(r['id'])
        
        # Запоминаем, кто куда зачислен
        for prog, lst in tentative.items():
            for a in lst:
                enrolled_program[a['id']] = prog
        
        self._enrolled = tentative
        self._enrolled_program = enrolled_program
        self._all_applicants = all_applicants
        
    def calculate_competition_stats(self):
        """Рассчитать конкурсную ситуацию."""
        self._run_admission()
        
        stats = {}
        for prog in self.capacity.keys():
            cap = self.capacity[prog]
            enrolled_count = len(self._enrolled[prog])
            
            # Сколько абитуриентов с согласием указали эту программу
            applicants_count = sum(
                1 for a in self._all_applicants.values()
                if a['consent'] and prog in a['priorities']
            )
            
            competition = applicants_count / cap if cap > 0 else 0
            status = 'НЕДОБОР' if enrolled_count < cap else 'НАБОР ЗАВЕРШЁН'
            
            stats[prog] = {
                'program_name': self.PROGRAM_NAMES.get(prog, prog),
                'capacity': cap,
                'enrolled_count': enrolled_count,
                'applicants_with_consent': applicants_count,
                'competition_ratio': round(competition, 2),
                'status': status
            }
        
        return stats
        
    def calculate_passing_score(self):
        """Определить проходной балл."""
        self._run_admission()
        
        scores = {}
        for prog in self.capacity.keys():
            enrolled = self._enrolled[prog]
            cap = self.capacity[prog]
            
            if len(enrolled) < cap or len(enrolled) == 0:
                scores[prog] = None  # недобор
            else:
                scores[prog] = enrolled[-1]['total']  # балл последнего
        
        return scores
        
    def generate_enrollment_lists(self):
        """Сформировать списки зачисленных."""
        self._run_admission()
        
        result = {}
        for prog in self.capacity.keys():
            result[prog] = [
                {
                    'id': a['id'],
                    'total': a['total'],
                    'math': a['math'],
                    'russian': a['russian'],
                    'physicsIct': a['physicsIct'],
                    'individual': a['individual'],
                    'priority': a['priorities'].get(prog, 0)
                }
                for a in self._enrolled[prog]
            ]
        
        return result
    
    def _generate_summary(self):
        """
        Сформировать полную сводку по всем требованиям ТЗ:
        1. Проходные баллы на ОП (или НЕДОБОР)
        2. Списки зачисленных с ID и суммой баллов
        3. Детальная статистика по приоритетам для каждой ОП
        """
        self._run_admission()
        
        passing_scores = self.calculate_passing_score()
        enrolled_lists = self.generate_enrollment_lists()
        
        # Детальная статистика по каждой ОП
        programs_stats = {}
        for prog in self.capacity.keys():
            # Подсчитываем заявления по приоритетам (среди всех абитуриентов с согласием)
            priority_applications = {1: 0, 2: 0, 3: 0, 4: 0}
            for a in self._all_applicants.values():
                if a['consent'] and prog in a['priorities']:
                    prio = a['priorities'][prog]
                    if prio in priority_applications:
                        priority_applications[prio] += 1
            
            # Подсчитываем зачисленных по приоритетам
            priority_enrolled = {1: 0, 2: 0, 3: 0, 4: 0}
            for applicant in self._enrolled[prog]:
                prio = applicant['priorities'].get(prog, 0)
                if prio in priority_enrolled:
                    priority_enrolled[prio] += 1
            
            total_applications = sum(priority_applications.values())
            
            programs_stats[prog] = {
                'program_name': self.PROGRAM_NAMES.get(prog, prog),
                'passing_score': passing_scores[prog] if passing_scores[prog] is not None else 'НЕДОБОР',
                'capacity': self.capacity[prog],
                'total_applications': total_applications,
                'applications_priority_1': priority_applications[1],
                'applications_priority_2': priority_applications[2],
                'applications_priority_3': priority_applications[3],
                'applications_priority_4': priority_applications[4],
                'enrolled_priority_1': priority_enrolled[1],
                'enrolled_priority_2': priority_enrolled[2],
                'enrolled_priority_3': priority_enrolled[3],
                'enrolled_priority_4': priority_enrolled[4],
                'total_enrolled': len(self._enrolled[prog]),
                'enrolled_list': enrolled_lists[prog]
            }
        
        return {
            'programs': programs_stats,
            'overall': {
                'total_capacity': sum(self.capacity.values()),
                'total_enrolled': sum(len(lst) for lst in self._enrolled.values()),
                'total_applicants_with_consent': sum(1 for a in self._all_applicants.values() if a['consent']),
                'programs_with_shortage': [p for p in self.capacity if len(self._enrolled[p]) < self.capacity[p]]
            }
        }
        
    def get_statistics_report(self, date_folder: str = None, save_to_reports: bool = False):
        """
        Получить сводную статистику.
        
        Args:
            date_folder: папка для сохранения отчёта (например "01-08")
            save_to_reports: если True, сохранить stats.json в reports/{date_folder}/
        """
        stats = {
            'competition': self.calculate_competition_stats(),
            'passing_score': self.calculate_passing_score(),
            'enrolled': self.generate_enrollment_lists(),
            'summary': self._generate_summary()
        }
        
        # Сохранение в reports/{date_folder}/stats.json
        if save_to_reports and date_folder:
            try:
                from pathlib import Path
                import json
                from datetime import datetime
                
                # Путь к папке reports
                base_dir = Path(__file__).parent.parent.parent / "data" / "reports" / date_folder
                base_dir.mkdir(parents=True, exist_ok=True)
                
                # Добавляем метаданные
                stats['_metadata'] = {
                    'generated_at': datetime.now().isoformat(),
                    'date_folder': date_folder
                }
                
                # Сохраняем
                stats_file = base_dir / "stats.json"
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                # Не прерываем выполнение при ошибке сохранения, но записываем ошибку
                import logging
                logger = logging.getLogger(__name__)
                logger.exception(f"Ошибка сохранения stats.json в {date_folder}: {e}")
                stats['save_error'] = str(e)
                stats['save_saved'] = False
            else:
                stats['save_saved'] = True

        return stats
    
    @staticmethod
    def calculate_dynamics(data_by_days: dict, capacity: dict) -> dict:
        """
        Рассчитать динамику проходных баллов по дням.
        
        Args:
            data_by_days: словарь {date: {program_code: [applicants]}}
            capacity: словарь {program_code: число мест}
            
        Returns:
            Словарь с динамикой проходных баллов по программам и дням
        """
        dynamics = {}
        dates = sorted(data_by_days.keys())
        
        for date in dates:
            manager = AdmissionManager(data_by_days[date], capacity)
            scores = manager.calculate_passing_score()
            
            for prog, score in scores.items():
                if prog not in dynamics:
                    dynamics[prog] = {
                        'program_name': AdmissionManager.PROGRAM_NAMES.get(prog, prog),
                        'by_date': {}
                    }
                dynamics[prog]['by_date'][date] = score if score is not None else 'НЕДОБОР'
        
        return dynamics



