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
        
        # Ключ сортировки по баллам (убывание), при равенстве — по ID (возрастание)
        def sort_key(a):
            return (-a['total'], -a['math'], -a['russian'], -a['physicsIct'], -a['individual'], a['id'])
        
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
        """Сформировать общую сводку."""
        self._run_admission()
        
        total_capacity = sum(self.capacity.values())
        total_enrolled = sum(len(lst) for lst in self._enrolled.values())
        total_applicants = sum(1 for a in self._all_applicants.values() if a['consent'])
        
        shortage = [p for p in self.capacity if len(self._enrolled[p]) < self.capacity[p]]
        
        return {
            'total_capacity': total_capacity,
            'total_enrolled': total_enrolled,
            'total_applicants_with_consent': total_applicants,
            'programs_with_shortage': shortage,
            'all_places_filled': total_enrolled == total_capacity
        }
        
    def get_statistics_report(self):
        """Получить сводную статистику."""
        stats = {
            'competition': self.calculate_competition_stats(),
            'passing_score': self.calculate_passing_score(),
            'enrolled': self.generate_enrollment_lists(),
            'summary': self._generate_summary()
        }
        return stats



